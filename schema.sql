DROP TABLE IF EXISTS `albums`;
CREATE TABLE `albums` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `artist` varchar(100) NOT NULL,
  `genre` varchar(50) NOT NULL,
  `year` year NOT NULL,
  `comment` varchar(100) DEFAULT NULL,
  `composer` varchar(50) DEFAULT NULL,
  `medium` enum('cd','digital','vinyl') NOT NULL,
  `type` enum('studio album','single','ep') NOT NULL,
  `complete` enum('y','n') NOT NULL,
  PRIMARY KEY (`id`)
)