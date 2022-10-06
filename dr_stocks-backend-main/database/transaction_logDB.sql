CREATE DATABASE IF NOT EXISTS `transaction_logDB` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `transaction_logDB`;

# TRANSACTION_LOGDB
DROP TABLE IF EXISTS `transaction_log`;
CREATE TABLE IF NOT EXISTS `transaction_log` (
  `transactionid` INT NOT NULL AUTO_INCREMENT,
  `accid` INT NOT NULL,
  `trade_accid` INT NOT NULL,
  `transaction_action` VARCHAR(20) NOT NULL,
  `transaction_value` DECIMAL(13, 2) NOT NULL,
  `transaction_date` DATETIME NOT NULL,
  `currency` CHAR(3) NOT NULL,
  `status` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`transactionid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `transaction_log` (`transactionid`, `accid`, `trade_accid`,`transaction_action`, `transaction_value`, `transaction_date`, `currency`,`status`) VALUES
('7000001', '1000001', '4000001','DEPOSIT', '1000.00', '2022-03-08 10:34:22', 'USD','SUCCESS'),
('7000002', '1000002', '4000002','DEPOSIT', '500.00', '2022-03-08 09:04:52', 'USD','SUCCESS');
COMMIT;

select * from transaction_logDB.transaction_log;
