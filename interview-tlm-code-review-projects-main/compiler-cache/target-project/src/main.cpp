#include <cxxopts.hpp>
#include <lib/lib.hpp>

int main(int argc, char**argv) {
  cxxopts::Options options("Sample", "Nothing Important");
  options.add_options()
      ("size", "Matrix size (int)", cxxopts::value<int>())
      ("scale", "Scale factor (double)", cxxopts::value<double>());
  options.parse_positional({"size", "scale"});

  auto const result{options.parse(argc, argv)};
  auto const size = result["size"].as<int>();
  auto const scale = result["scale"].as<double>();

  lib::entryPoint(size, scale);

  return 0;
}
