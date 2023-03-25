// Set permission to write data
sudo chown -R logstash.logstash /usr/share/logstash
sudo chmod 777 /usr/share/logstash/data

// Set permission to write to Gemfile
sudo chmod -R 777 /usr/share/logstash

// install sqlite input plugin
bin/logstash-plugin install logstash-input-sqlite

bin/logstash-plugin install logstash-input-jdbc



