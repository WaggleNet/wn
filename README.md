# The WaggleNet Uber-Command: `wn`

So we thought that setting up environments are a nightmare. So we were constantly annoyed at configurating all the moving pieces just to get marginally wagglin'. So y'all blame the team leaders for not writing docs and yeah they kinda deserve it. But, so what??

Introducing the heavenly WaggleNet command - `wn`. It's a bold automation project aiming at setting up WaggleNet and housekeeping all the pieces quickly and easily.

## Getting started.

Sorry, Windows not supported. For better experience you can use [Ubuntu on Windows](https://tutorials.ubuntu.com/tutorial/tutorial-ubuntu-on-windows#0). Now you have Linux or Unix (pronouced: "Mac"). Give this command a try:

```bash
sh -c "$(curl -sSL https://raw.githubusercontent.com/WaggleNet/wn/master/install.sh?$(date +%s))"
```

And follow the instruction.

## What can I do with this thing?

First startup, you'll need to configure it. The command is `wn config`. If you forgot to do it, it'll ask you each time. Basically there are three things you need to do,

- Give it a nice directory for it to store all the code. If you use a Mac (or some Linux) you can just drag the folder in.
- Give it your Github username.
- Give it your Github password. WARNING: It's stored in plaintext. If you don't want that, you can opt to type in the password each time instead.

Welcome to WaggleNet (again and again). You're now able to do the following: (**note**. Actually not all of them. We're trying as hard as we can to bring all the functions out but YMMV. Refer to the command output for actual capabilities for the time being.)

## Code stuff

For details of what you can do, run `wn code`.

You can set up some projects just by doing:
- `wn code init iam` for a specific project such as IAM
- `wn code init serv` for bringing up the whole stack such as SERV

Bringing up means the following things actually:
- Checking if you have the necessary tools installed already.
- Git cloning the repo.
- Creating virtual environments and installing dependencies.
- Performing initial database migration.
- Generating configuration files to link projects together.

And for housekeeping you can do the following. Apparently, you can swap `iam` for anything mentioned above, even if it's a group of projects.
- `wn code update iam git` for pulling Git repository.
- `wn code update iam db` for running DB migration.
- `wn code update iam env` for updating dependencies such as pip and node modules.
- Or just use `wn code update iam` for all the above.

If you want to work on a different branch:
- `wn code checkout serv master` switches all the `serv` projects to master branch.

Then you can also get the location of the project so you can do:
- `atom $(wn where iam)` to open IAM project using Atom.
