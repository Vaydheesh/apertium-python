CXX = g++
h_sources = alphabet.h att_compiler.h buffer.h compiler.h compression.h  \
            deserialiser.h entry_token.h expander.h fst_processor.h lt_locale.h \
            ltstr.h match_exe.h match_node.h match_state.h my_stdio.h node.h \
            pattern_list.h regexp_compiler.h serialiser.h sorted_vector.h state.h \
            transducer.h trans_exe.h xml_parse_util.h exception.h tmx_compiler.h \
            string_to_wostream.h
cc_sources = alphabet.cc att_compiler.cc compiler.cc compression.cc entry_token.cc \
             expander.cc fst_processor.cc lt_locale.cc match_exe.cc \
             match_node.cc match_state.cc node.cc pattern_list.cc \
             regexp_compiler.cc sorted_vector.cc state.cc transducer.cc \
             trans_exe.cc xml_parse_util.cc tmx_compiler.cc
obj_sources = $(cc_sources:.cc=.o)
ODIR = ./lttoolbox/lttoolbox
OBJS = $(patsubst %,$(ODIR)/%,$(obj_sources))

CFLAGS = -O2 -fPIC -c
INCLUDES = -I../swig/lttoolbox
PYINCLUDE = -I/usr/include/python3.7m 
XMLINCLUDE = -I/usr/include/libxml2
LFLAGS = -L/usr/include/libxml2
LIBS = -lxml2 -lm
SWIGFLAGS = -python -c++ -Wall
MAIN = analysis
SWIGFILE = $(MAIN).i
SHAREDLIB = _$(MAIN).so
PYTHONFILE = $(MAIN).py
WRAPPERCXX = $(MAIN)_wrap.cxx
WRAPPEROBJ = $(WRAPPERCXX:.cxx=.o)

all: $(PYTHONFILE) $(SHAREDLIB)

$(PYTHONFILE): $(WRAPPERCXX) $(WRAPPEROBJ)

$(WRAPPERCXX): $(SWIGFILE)
	swig $(SWIGFLAGS) $(INCLUDES) $(SWIGFILE)

$(WRAPPEROBJ): $(WRAPPERCXX)
	$(CXX) $(CFLAGS) $(INCLUDES) $(XMLINCLUDE) -c $(WRAPPERCXX) $(PYINCLUDE)

$(SHAREDLIB): obj_sources
	$(CXX) -shared $(WRAPPEROBJ) $(OBJS) -o $(SHAREDLIB) $(LIBS)

obj_sources:
	$(MAKE) -C ./lttoolbox/lttoolbox

clean:
	$(RM) $(SHAREDLIB) $(PYTHONFILE) $(WRAPPERCXX) $(WRAPPEROBJ) 
	$(RM) -r __pycache__
	$(MAKE) clean -C ./lttoolbox/lttoolbox
