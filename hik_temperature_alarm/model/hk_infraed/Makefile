CC       = gcc
CXX      = g++
CFLAGS   = -g
CXXFLAGS = $(CFLAGS)

LIBPATH = ./
LIBS = -Wl,-rpath=./:./HCNetSDKCom -lhcnetsdk
SRC = ./temperature_now.cpp
TARGET = ./getpsdata_now.so

all: 
	$(CXX) $(OPTI) $(CXXFLAGS) -shared -fPIC $(SRC) -o $(TARGET) -L$(LIBPATH) $(LIBS)

.PHONY: clean
clean:
	rm -f $(TARGET)
