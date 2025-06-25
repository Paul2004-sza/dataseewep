CREATE DATABASE data_app;
USE data_app;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `data_file` (
  `id` int NOT NULL AUTO_INCREMENT,
  `filename` varchar(256) NOT NULL,
  `filepath` varchar(512) NOT NULL,
  `uploaded_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `data_file_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `analysis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `data_file_id` int NOT NULL,
  `analysis_type` varchar(128) NOT NULL,
  `parameters` text,
  `result_path` varchar(512) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `data_file_id` (`data_file_id`),
  CONSTRAINT `analysis_ibfk_1` FOREIGN KEY (`data_file_id`) REFERENCES `data_file` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `prediction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `data_file_id` int NOT NULL,
  `model_type` varchar(128) NOT NULL,
  `target_column` varchar(128) NOT NULL,
  `parameters` text,
  `metrics` text,
  `result_path` varchar(512) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `data_file_id` (`data_file_id`),
  CONSTRAINT `prediction_ibfk_1` FOREIGN KEY (`data_file_id`) REFERENCES `data_file` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
