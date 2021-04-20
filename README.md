# interceptor

A tool to intercept calls to your command line tools and alter their args.

Requires UNIX and working Python3 and whereis.

## Installation

Since the `interceptor` PyPI package name is taken, 
you ought to install interceptor the following way:

```bash
pip install git+https://github.com/Cervi-Robotics/interceptor.git
```

Or, if you don't have pip:

```bash
git clone https://github.com/Cervi-Robotics/interceptor.git
cd interceptor
python setup.py install
```

## Usage

### Prepare the configuration

To override g++ put a JSON file at `/etc/interceptor.d/g++`

with the following contents:

```json
{
  "args_to_take_away": ["-quiet"],
  "args_to_append": ["-DDEBUG"]],
  "args_to_append_before": ["-v"],
  "args_to_replace": [["-march=native", "-mcpu=native"]],
  "display_before_start": true
}
```

#### Configuring

If the intercepted command sees any arguments given in 
`args_to_take_away` they will be removed before being passed to target command.

If arguments in `args_to_append` are not in arguments, 
they will be appended to the arguments.

If arguments in `args_to_append_before` are not in arguments,
they will be prepended to arguments.

You give two-item lists in `args_to_replace`. If
the first item occurs in arguments, it will be replaced by the second item. 

If you don't prepare the configuration file in advance, an empty file will be created for you.
     
If `display_before_start` is set, then before the launch
the application name and parameters actually passed to it will be displayed on stdout.
     
### The intercept command

The `intercept` command is the basic command used to interface with interceptor.

#### Intercepting tools

Say, to intercept the command `foo` invoke:

```bash
intercept foo
```

Interceptor should display the following:

```
Successfully intercepted foo
```

A Python wrapper will be found at previous location of 
foo, while it itself will be copied to the same directory
but named `foo-intercepted`.
The wrapper will hold the name of `foo` inside, 
so you can symlink it safely (eg. symlink of g++ to c++).

To cancel intercepting `foo` type:

```bash
intercept undo foo
```
