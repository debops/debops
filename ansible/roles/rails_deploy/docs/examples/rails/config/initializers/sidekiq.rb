sidekiq_config = {
  url: ENV['BACKGROUND_URL'],
  namespace: "yourappname::sidekiq_#{Rails.env}"
}

Sidekiq.configure_server do |config|
  config.redis = sidekiq_config
end

Sidekiq.configure_client do |config|
  config.redis = sidekiq_config
end
