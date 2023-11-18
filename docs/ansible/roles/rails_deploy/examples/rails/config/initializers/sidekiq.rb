# Copyright (C) 2014      Nick Janetakis <nickjanetakis@gmail.com>
# Copyright (C) 2014-2019 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2015-2019 DebOps Project <http://debops.org/>
# SPDX-License-Identifier: GPL-3.0-only

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
