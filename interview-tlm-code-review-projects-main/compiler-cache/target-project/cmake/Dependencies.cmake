include(FetchContent)

FetchContent_Declare(
        cxxopts
        GIT_REPOSITORY https://github.com/jarro2783/cxxopts.git
        GIT_TAG v3.2.0
        GIT_SHALLOW ON
)
FetchContent_Declare(
        eigen
        GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
        GIT_TAG nightly # Last release is too old
        GIT_SHALLOW ON
)

FetchContent_MakeAvailable(cxxopts eigen)
