%module analysis 

%{
#define SWIG_FILE_WITH_INIT
#include "fst_processor.h"
#include "lttoolbox_config.h"
#include "my_stdio.h"
#include "lt_locale.h"

#define EXIT_FAILURE  1 /* Failing exit status.  */

class FST: private FSTProcessor
{
private:
  void check_validity();

public:
  /**
   * Reads from input_path and stores result at output_path
   */  
  void init_analysis(char *automorf_path, char *input_path, char *output_path);
};

void 
FST::check_validity()
{
  if(!valid())
  {
      exit(EXIT_FAILURE);
  }
}

void 
FST::init_analysis(char *automorf_path, char *input_path, char *output_path)
{
  setDictionaryCaseMode(true);
  LtLocale::tryToSetLocale();
  FILE *in = fopen(automorf_path, "rb");
  load(in);
  initAnalysis();
  check_validity();
  FILE *input = fopen(input_path, "r"), *output = fopen(output_path, "w");
  analysis(input, output);
  fclose(in);
  fclose(input);
  fclose(output);
}

%}


%include "fst_processor.h"
%include "lttoolbox_config.h"
%include "my_stdio.h"
%include "lt_locale.h"

class FST: private FSTProcessor
{
private:
  void check_validity();

public:
  /**
   * Reads from input_path and stores result at output_path
   */  
  void init_analysis(char *automorf_path, char *input_path, char *output_path);
};
