INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_RFFE_CTL rffe_ctl)

FIND_PATH(
    RFFE_CTL_INCLUDE_DIRS
    NAMES rffe_ctl/api.h
    HINTS $ENV{RFFE_CTL_DIR}/include
        ${PC_RFFE_CTL_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    RFFE_CTL_LIBRARIES
    NAMES gnuradio-rffe_ctl
    HINTS $ENV{RFFE_CTL_DIR}/lib
        ${PC_RFFE_CTL_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(RFFE_CTL DEFAULT_MSG RFFE_CTL_LIBRARIES RFFE_CTL_INCLUDE_DIRS)
MARK_AS_ADVANCED(RFFE_CTL_LIBRARIES RFFE_CTL_INCLUDE_DIRS)

