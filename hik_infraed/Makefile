CC       = gcc
CXX      = g++
CFLAGS   = -g
CXXFLAGS = $(CFLAGS)

LIBPATH = ./
LIBS = -Wl,-rpath=./:./HCNetSDKCom -lhcnetsdk -lmysqlclient
SRC = ./infraed.cpp
TARGET = ./getpsdata_infraed.so

all: 
	$(CXX) $(OPTI) $(CXXFLAGS) -shared -fPIC $(SRC) -o $(TARGET) -L$(LIBPATH) $(LIBS)

.PHONY: clean
clean:
	rm -f $(TARGET)
