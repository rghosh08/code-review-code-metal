#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <unordered_map>
#include <vector>

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <sys/stat.h>

#define RAPIDJSON_HAS_STDSTRING 1
#include "rapidjson/document.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"
#include "rapidjson/filewritestream.h"

using std::string;
using std::vector;
using std::filesystem::path;
using namespace std::filesystem;
using namespace rapidjson;


// Check whether we have a cached copy newer than the dependencies
// Afterwards, compilation_unit will be a path to where the new object file should be.
bool cacheHit (const Document& d, const string& build_command, path* bin_out);

// Copy the artifact back from cache.
void fetchArtifact (const path& compilation_unit, const string& build_command);

// extract the build dependencies; this uses the json profile emitted by clang.
vector<path> extractDeps(const string& deps, path * build_output);

// the path where the build output from this command would go.
// It's based on a hash of the build command. New command, new path.
path cachedFilePath(const string& build_command);

//  Update the cache record, in memory.
void updateCache(Document& cache_state, const vector<path>& deps, time_t build_time, const string& build_cmd, const path& compilation_unit);

// Write the cache to filesystem.
void writeCache(Document& cache_state); 


path CACHE_PATH = "/tmp/buildcache/cache.json";


int main (int argc, char **argv) {
  std::cout << "Args:\n";
  string build_cmd = argv[1];
  bool next_is_depfile = false;
  string depfile = "";
  for (int i = 2; i < argc; ++i) {
    std::cout << i << "] " << argv[i] << std::endl;
    build_cmd.append (" ");
    build_cmd.append (argv[i]);
    if (next_is_depfile) {
      depfile = argv[i];
    } 
    next_is_depfile = (strcmp(argv[i], "-MF") == 0);
  }
  if (depfile == "") {
    std::cout << "ERR: no dependency file found\n";
    exit(1);
  }

  Document cache_state;
  if (std::filesystem::is_regular_file(CACHE_PATH)) {
    std::stringstream buffer;
    buffer << std::ifstream( string(CACHE_PATH) ).rdbuf();
    cache_state.Parse(buffer.str().c_str());
  } else {
    cache_state.SetArray();
    std::filesystem::create_directories(CACHE_PATH.parent_path());
  }

  path original_bin_path;
  if (cacheHit (cache_state, build_cmd, &original_bin_path)) {
    fetchArtifact (original_bin_path, build_cmd);
  } else {
    path compilation_unit; // the .cpp file being built

    std::cout << "cache miss, rebuilding object.\n";
    time_t build_time;
    time(&build_time);
    int rc = system(build_cmd.c_str());
    if (rc != 0) return rc;
    std::cout << "reading dependencies from " << depfile << std::endl;
    vector<path> deps = extractDeps(depfile, &original_bin_path);

    path new_path = cachedFilePath(build_cmd); 
    std::cout << "caching " << original_bin_path << " to " << new_path << std::endl;
    std::filesystem::copy(original_bin_path, new_path, std::filesystem::copy_options::update_existing);
    updateCache(cache_state, deps, build_time, build_cmd, original_bin_path);
    writeCache(cache_state);
  }  
}

vector<path> extractDeps(const string& dependency_file, path * build_output) {
  std::ifstream dependency;
  dependency.open (dependency_file);
  string line;
  vector<path> deps;  

  std::getline(dependency, line);
  line = line.substr(0, line.rfind(':'));
  std::cout << "build output was " << line << std::endl;
  *build_output = std::filesystem::absolute(path(line));

  while (std::getline(dependency, line)) {
    line = line.substr(line.find('/'));
    line = line.substr(0, line.find(' '));
//    std::cout<< "dep is '" << line << "'\n";
    deps.push_back( std::filesystem::weakly_canonical(line));
  }
  std::cout << "found " << deps.size() << " deps" << std::endl;
  return deps;
}

// This was basically from the rapidjson docs
 void writeCache(Document& cache_state) {
  FILE* fp = fopen(CACHE_PATH.c_str(), "wb"); // non-Windows use "w"
	  
  char write_buffer[65536];
  FileWriteStream os(fp, write_buffer, sizeof(write_buffer));
	  
  Writer<FileWriteStream> writer(os);
  cache_state.Accept(writer);	  
  fclose(fp);
}

void updateCache(Document& cache_state, const vector<path>& deps, time_t build_time, const string& build_cmd, const path& build_out) {
  Value to_update(kObjectType);
  Document::AllocatorType& allocator = cache_state.GetAllocator();

  to_update.AddMember("cmd", build_cmd, allocator);
  to_update.AddMember("time", build_time, allocator);
  Value build_out_value;
  build_out_value.SetString(string(build_out), allocator);
  to_update.AddMember("target_o", build_out_value, allocator);
  Value deps_value(kArrayType);
  for (const auto& path : deps) {
    deps_value.PushBack(Value(string(path), allocator), allocator);
  }
  to_update.AddMember("deps", deps_value, allocator);

  for ( auto& row : cache_state.GetArray()) {
    if (row["cmd"] == build_cmd) {
      row = to_update;
      return;
    }
  } 
  cache_state.PushBack(to_update, allocator);  
}


bool cacheHit (const Document& cache_state, const string & build_cmd, path * bin_out) {
  struct stat file_stat;
  std::cout << "Cache has " << cache_state.Size() << " entries. Seeking '"<< build_cmd <<"' \n";
  
  for ( auto& row : cache_state.GetArray()) {
    std::cout << "row: " << row["cmd"].GetString() << std::endl;
    if (row["cmd"] == build_cmd) {
      time_t build_time = row["time"].GetUint64();
      std::cout << "row matched, looking for files changed since " << build_time << std::endl;
      for ( auto& f : row["deps"].GetArray() ) {
        string dependency = f.GetString();	
        int rc = stat(dependency.c_str(), &file_stat);
        if ( rc == 0  && S_ISREG(file_stat.st_mode) ) {
          if ( file_stat.st_mtime > build_time) {
            std::cout << "file " << dependency << "updated too recently\n";
            return false;
          }
        } else {
          std::cout<< "Warning: can't read '" << dependency  << "' mode was " << file_stat.st_mode << std::endl;
        }		
      }
      *bin_out = path(row["target_o"].GetString());
      return true;
    }
  }
  return false;
}

void fetchArtifact (const path& dest, const string & build_cmd) {
  path cached = cachedFilePath(build_cmd);
  std::cout << "copying " << cached << " to " << dest << std::endl;
  std::filesystem::copy(cached, dest, std::filesystem::copy_options::overwrite_existing);
}

path cachedFilePath(const string& build_command) {
  path p = CACHE_PATH.parent_path() / std::to_string(std::hash<std::string>{}(build_command));
  p += ".o";
  return p; 
}
