# Waveshare Modbus POE ETH Relay Controller

This Python script provides a command-line interface to control and query the state of a Waveshare Modbus POE ETH 8ch Relay. The script allows you to turn relays on/off, flip their state, flash them for a specified duration, and retrieve the current state of all relays.

## Prerequisites

- Python 3.x
- A Modbus POE ETH Relay device connected to your network.

## Usage

1. Clone this repository or download the script.
2. Navigate to the directory containing the script.
3. Run the script using Python:

```
python3 relay.py [OPTIONS]
```

### Options:

- `--host`: IP address of the Relay host. 
- `--port`: Port number to connect to. Default is `4196`.
- `--loglevel`: Set the log level. Default is `INFO`.

### Commands:

- **relay**: Control individual or all relays.
  - `number`: Relay number (1-8). Use `256` for all relays.
  - `action`: Action to perform (`on`, `off`, `flip`).

  Example:
  ```
  python3 relay.py relay 1 on
  ```

- **flash**: Flash a relay for a specified duration.
  - `number`: Relay number (1-8).
  - `action`: Flash action (`on`, `off`).
  - `duration`: Duration of the flash action in 100ms increments. For example, `10` equals 1 second. Range: 1-65535.

  Example:
  ```
  python3 relay.py flash 1 on 10
  ```

- **state**: Retrieve the current state of all relays.

  Example:
  ```
  python3 relay.py state
  
  [false, false, true, true, true, true, true, false]
  ```


## References

For more details about the Waveshare Modbus POE ETH Relay, visit the [official documentation](https://www.waveshare.com/wiki/Modbus_POE_ETH_Relay).

## License

This project is open-source. Feel free to modify, distribute, and use it as per your requirements.
