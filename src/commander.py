import os
import re
import subprocess
import shlex
from discord.ext import commands
from pathlib import Path  # Python 3.6+ only


discord_token=os.getenv("DISCORD_TOKEN")
print(discord_token)
bot = commands.Bot(command_prefix="!")

class ComposeError(Exception):
    pass

class ComposeService():
    def __init__(self, compose_file):
        self.compose_file = compose_file

    def is_up(self, verbose=False):
        stdout = self._ps()
        # remove the header and dashes
        headerless = stdout.split("\n")[4]
        # split into segments
        split = [i.strip() for i in headerless.split('  ') if i]
        # get the segments we need
        container = split[0]
        status = split[2]

        # form the final message for discord
        up = False
        message = "The server is not started. `!start` to start it. Don't forget to login to host to launch farm."
        if "Up" in status:
            up = True 
            message = "The server is running."
        elif "Paused" in status:
            up = False
            message = "The server is paused. `!unpause` to resume."
        if verbose:
            message = f"{message}\n```{stdout}```"
        return up, message

    def start(self, verbose=False):
        if self.is_up()[0]:
            return "The server is already started sillyhead."
        compose_cmd = "start"
        stdout = self._compose_exec(compose_cmd)
        message = "The server is starting up..."
        if verbose:
            message = f"{message}\n```{stdout}```"
        return message

    def pause(self, verbose=False):
        compose_cmd = "pause"
        stdout = self._compose_exec(compose_cmd)
        message = "The server is paused."
        if verbose:
            message = f"{message}\n```{stdout}```"
        return message

    def unpause(self, verbose=False):
        compose_cmd = "unpause"
        stdout = self._compose_exec(compose_cmd)
        message = "The server is unpaused."
        if verbose:
            message = f"{message}\n```{stdout}```"
        return message

    def stop(self, verbose=False):
        if not self.is_up()[0]:
            return "The server is already stopped funny goose."
        compose_cmd = "stop"
        stdout = self._compose_exec(compose_cmd)
        message = "The server is stopping..."
        if verbose:
            message = f"{message}\n```{stdout}```"
        return message

    def _ps(self):
        compose_cmd = "ps"
        stdout = self._compose_exec("ps")
        return stdout

    def _compose_exec(self, compose_cmd):
        base_cmd = ["docker-compose", "-f", self.compose_file]
        compose_cmd = shlex.split(compose_cmd)
        cmd = base_cmd + compose_cmd
        resp = subprocess.run(cmd, capture_output=True)
        stdout = resp.stdout.decode('UTF-8')
        stderr = resp.stderr.decode('UTF-8')
        if resp.returncode != 0:
            print(cmd)
            print(resp.returncode, stderr, stdout)
            raise ComposeError("Command failed. check my logs for details.")
        
        stdout = f"> {' '.join(cmd)}\n\n{stdout}"
        return stdout


stardew = ComposeService(os.getenv("DOCKER_COMPOSE_FILE"))
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def status(ctx, *args):
    verbose = "verbose" in args
    is_up, message = stardew.is_up(verbose=verbose)

    await ctx.send(message)

@bot.command()
async def start(ctx, *args):
    verbose = "verbose" in args
    message = stardew.start(verbose=verbose)

    await ctx.send(message)

@bot.command()
async def stop(ctx, *args):
    verbose = "verbose" in args
    message = stardew.stop(verbose=verbose)

    await ctx.send(message)

@bot.command()
async def pause(ctx, *args):
    verbose = "verbose" in args
    message = stardew.stop(verbose=verbose)

    await ctx.send(message)

@bot.command()
async def unpause(ctx, *args):
    verbose = "verbose" in args
    message = stardew.stop(verbose=verbose)

    await ctx.send(message)

bot.run(discord_token)