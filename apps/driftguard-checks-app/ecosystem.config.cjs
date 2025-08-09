module.exports = {
  apps: [{
    name: 'driftguard-checks',
    script: 'lib/index.js',
    watch: false,
    instances: 1,
    autorestart: true,
    max_memory_restart: '500M',
    env_file: '.env',
    env: {
      NODE_ENV: 'production',
      PORT: 3001
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2-combined.log',
    time: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    kill_timeout: 5000,
    listen_timeout: 10000
  }]
};
