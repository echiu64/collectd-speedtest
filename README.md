= Collectd speedtest.net plugin

== Pre-reqs
 * Speedtest CLI from Ookla - https://www.speedtest.net/apps/cli
    * remove any other `speedtest` version that you may have

== Tested Platforms
 * Ubuntu 16.04.6 LTS
 * collectd 5.5.1-1build2

== Install
 * See `speedtest.conf` 
   * use `speedlist -L` to find and pick your serverse to test
 * Run `speedtest` as the collectd user first to accept the terms
   * you will see a file in `~/.config/ookla/speedtest-cli.json` if accepted

