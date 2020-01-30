def run(cmd):
        logger.debug(
        "run_cmd: run: the commandline is %s",
        cmd.encode("unicode_escape").decode("utf-8"),
    )
    out = subprocess.Popen(
        (cmd),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    stdout, stderr = out.communicate()
    if stderr is None:
        logger.debug("run_cmd: run: Read: %s", stdout.decode("utf-8"))
        return(0)
    else:
        logger.error(
            "run_cmd: run: could not run"
        )
        return(1)
