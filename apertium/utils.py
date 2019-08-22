import os
import platform
import subprocess
import sys
import tempfile
from typing import List

try:
    if platform.system() == 'Linux':
        sys.path.append('/usr/lib/python3/dist-packages')

    import apertium_core
    import lextools
    import lttoolbox
    import constraint_grammar
    wrappers_available = True
except ImportError:
    wrappers_available = False

import apertium  # noqa: F401
from apertium.iso639 import iso_639_codes

iso639_codes_inverse = {v: k for k, v in iso_639_codes.items()}


def to_alpha3_code(code: str) -> str:
    """
    Args:
        code (str)

    Returns:
        str
    """
    if '_' in code:
        code, variant = code.split('_')
        return '%s_%s' % ((iso639_codes_inverse[code], variant) if code in iso639_codes_inverse else (code, variant))
    else:
        return iso639_codes_inverse[code] if code in iso639_codes_inverse else code


def execute_pipeline(inp: str, commands: List[List[str]]) -> str:
    """
    Executes the given list of commands and returns the final output

    Returns:
        str
    """
    end = inp.encode()
    for command in commands:
        # On Windows, a NamedTemporaryFile with delete=True can only be opened once.
        # Since the file is opened both by Python and the C++ SWIG wrappers, we use
        # delete=False and manually delete the file.
        used_wrapper = True
        if wrappers_available:
            input_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
            output_file = tempfile.NamedTemporaryFile(delete=False)
            input_file_name, output_file_name = input_file.name, output_file.name

            arg = command[1][1] if len(command) >= 3 else ''
            text = end.decode()
            input_file.write(text)
            input_file.close()

            if 'lt-proc' == command[0] and '-w' == command[1]:
                dictionary_path = command[-1]
                dictionary = lttoolbox.fopen(dictionary_path, 'rb')

                lttoolbox.LtLocale.tryToSetLocale()
                fstp = lttoolbox.FSTProcessor()
                fstp.load(dictionary)
                lttoolbox.fclose(dictionary)

                fstp.initAnalysis()
                if not fstp.valid():
                    raise ValueError('FST Invalid')
                input_pointer = lttoolbox.fopen(input_file.name, 'r')
                output_pointer = lttoolbox.fopen(output_file.name, 'w')
                fstp.analysis(input_pointer, output_pointer)
                lttoolbox.fclose(input_pointer)
                lttoolbox.fclose(output_pointer)
            elif 'lrx-proc' == command[0]:
                dictionary_path = command[-1]
                lextools.LtLocale.tryToSetLocale()
                lrx = lextools.LRXProc(dictionary_path)
                lrx.lrx_proc(arg, input_file.name, output_file.name)
            elif 'apertium-transfer' == command[0]:
                transfer = apertium_core.ApertiumTransfer(command[2], command[3])
                transfer.transfer_text(arg, input_file.name, output_file.name)
            elif 'apertium-interchunk' == command[0]:
                interchunk = apertium_core.ApertiumInterchunk(command[1], command[2])
                interchunk.interchunk_text(arg, input_file.name, output_file.name)
            elif 'apertium-postchunk' == command[0]:
                postchunk = apertium_core.ApertiumPostchunk(command[1], command[2])
                postchunk.postchunk_text(arg, input_file.name, output_file.name)
            elif 'apertium-pretransfer' == command[0]:
                apertium_core.pretransfer(arg, input_file.name, output_file.name)
            elif 'apertium-tagger' == command[0]:
                command += [input_file.name, output_file.name]
                apertium_core.ApertiumTagger(len(command), command)
            elif 'cg-proc' == command[0]:
                dictionary_path = command[-1]
                cg = constraint_grammar.CGProc(dictionary_path)
                cg_proc_command = command[:-1]
                cg.cg_proc(len(cg_proc_command), cg_proc_command, input_file.name, output_file.name)
            else:
                used_wrapper = False

            if used_wrapper:
                output_file.seek(0)
                end = output_file.read()
            output_file.close()

            os.remove(input_file_name)
            os.remove(output_file_name)
        if not wrappers_available or not used_wrapper:
            apertium.logger.warning('Calling subprocess %s', command[0])
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            end, _ = proc.communicate(end)
    return end.decode()


def parse_mode_file(mode_path: str) -> List[List[str]]:
    """
    Args:
        mode_path (str)

    Returns:
        List[List[str]]
    """
    with open(mode_path) as mode_file:
        mode_str = mode_file.read().strip()
    if mode_str:
        commands = []
        for cmd in mode_str.strip().split('|'):
            # TODO: we should make language pairs install
            # modes.xml instead; this is brittle (what if a path
            # has | or ' in it?)
            cmd = cmd.replace('$2', '').replace('$1', '-g')
            commands.append([c.strip("'") for c in cmd.split()])
        return commands
    else:
        raise apertium.ModeNotInstalled(mode_path)
