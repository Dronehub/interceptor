# interceptor

A tool to intercept calls to your command line tools and alter their args

Requires UNIX and working Python3 and whereis.

## Usage

### Prepare the configuration

To override g++ put a JSON file at `/etc/interceptor.d/g++`

with the following contents:

```json
{
  "args_to_take_away": ["-quiet"],
  "args_to_append": ["-DDEBUG"]],
  "args_to_append_before": ["-v"],
  "args_to_replace": [["-march=native", "-mcpu=native"]]
}
```
     
### Launch interceptor

And then invoke

```bash
intercept g++
```

Interceptor should display the following:

```
Successfully intercepted g++
```

A Python wrapper will be found at previous location of 
g++, while it itself will be copied to the same directory
but named `g++-intercepted`.
