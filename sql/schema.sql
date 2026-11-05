-- Select smart_logistics_bengaluru before running. No DROP/DELETE/ALTER statements.
CREATE TABLE IF NOT EXISTS locations (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  x DOUBLE NOT NULL,
  y DOUBLE NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS roads (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  source_id INT NOT NULL,
  target_id INT NOT NULL,
  speed_kmph DOUBLE NOT NULL,
  UNIQUE KEY uq_road_pair (source_id, target_id),
  FOREIGN KEY (source_id) REFERENCES locations(id),
  FOREIGN KEY (target_id) REFERENCES locations(id),
  CHECK (speed_kmph > 0),
  CHECK (source_id <> target_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS route_history (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  source_id INT NOT NULL,
  target_id INT NOT NULL,
  mode ENUM('shortest', 'fastest') NOT NULL,
  path_json JSON NOT NULL,
  distance_km DOUBLE NOT NULL,
  duration_minutes DOUBLE NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (source_id) REFERENCES locations(id),
  FOREIGN KEY (target_id) REFERENCES locations(id)
) ENGINE=InnoDB;
