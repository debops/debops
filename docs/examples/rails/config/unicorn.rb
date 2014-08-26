# Heavily inspired by gitlab:
# https://github.com/gitlabhq/gitlabhq/blob/master/config/unicorn.rb.example

# Go with at least 1 per CPU core, a higher amount will usually help for fast
# responses such as reading from a cache.
worker_processes ENV['WORKERS'].to_i

# Listen on a tcp port or unix socket.
if ENV['LISTEN_ON'].include?(':')
  listen ENV['LISTEN_ON']
else
  # Use a shorter socket backlog for quicker failover when busy.
  listen ENV['LISTEN_ON'], backlog: 64
end

# The path where the pid file will be written to.
pid "#{ENV['RUN_STATE_PATH']}/#{ENV['SERVICE']}.pid"

# Use a shorter timeout instead of the 60s default. If you are handling large
# uploads you may want to increase this.
timeout 30

# The file that gets logged to.
stdout_path ENV['LOG_FILE']
stderr_path ENV['LOG_FILE']

# Combine Ruby 2.0.0dev or REE with "preload_app true" for memory savings:
# http://rubyenterpriseedition.com/faq.html#adapt_apps_for_cow
preload_app true
GC.respond_to?(:copy_on_write_friendly=) and
  GC.copy_on_write_friendly = true

# Enable this flag to have unicorn test client connections by writing the
# beginning of the HTTP headers before calling the application. This
# prevents calling the application for connections that have disconnected
# while queued. This is only guaranteed to detect clients on the same
# host unicorn runs on, and unlikely to detect disconnects even on a
# fast LAN.
check_client_connection false

before_fork do |server, worker|
  # Don't bother having the master process hang onto older connections.
  defined?(ActiveRecord::Base) and
    ActiveRecord::Base.connection.disconnect!

  # The following is only recommended for memory/DB-constrained
  # installations. It is not needed if your system can house
  # twice as many worker_processes as you have configured.
  #
  # This allows a new master process to incrementally
  # phase out the old master process with SIGTTOU to avoid a
  # thundering herd (especially in the "preload_app false" case)
  # when doing a transparent upgrade. The last worker spawned
  # will then kill off the old master process with a SIGQUIT.
  old_pid = "#{server.config[:pid]}.oldbin"
  if old_pid != server.pid
    begin
      sig = (worker.nr + 1) >= server.worker_processes ? :QUIT : :TTOU
      Process.kill(sig, File.read(old_pid).to_i)
    rescue Errno::ENOENT, Errno::ESRCH
    end
  end

  # Throttle the master from forking too quickly by sleeping. Due
  # to the implementation of standard Unix signal handlers, this
  # helps (but does not completely) prevent identical, repeated signals
  # from being lost when the receiving process is busy.
  # sleep 1
end

after_fork do |server, worker|
  # Per-process listener ports for debugging, admin, migrations, etc..
  # addr = "127.0.0.1:#{9293 + worker.nr}"
  # server.listen(addr, tries: -1, delay: 5, tcp_nopush: true)

  defined?(ActiveRecord::Base) and
    ActiveRecord::Base.establish_connection

  # If preload_app is true, then you may also want to check and
  # restart any other shared sockets/descriptors such as Memcached,
  # and Redis. TokyoCabinet file handles are safe to reuse
  # between any number of forked children (assuming your kernel
  # correctly implements pread()/pwrite() system calls).
end
