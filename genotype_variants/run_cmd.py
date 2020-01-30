import logging
import subprocess
"""
run_cmd
~~~~~~~~~~~~~~~
:Description: Code to run shell commands 
"""
"""
Created on January 29, 2020
Description: Code to run shell commands
@author: Ronak H Shah
"""
# Making logging possible
logger = logging.getLogger("genotype_variants")

def run_cmd(cmd):
    """Code to run shell commands"""
    logger.debug(
        "run_cmd: run: the command line is %s",
        cmd.encode("unicode_escape").decode("utf-8"),
    )
    out = subprocess.Popen(
        (cmd),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    out.wait()
    stdout, stderr = out.communicate()
    if stderr is None:
        logger.debug("run_cmd: run: Read: %s", stdout.decode("utf-8"))
    else:
        logger.error(
            "run_cmd: run: could not run"
        )
    return(out)
