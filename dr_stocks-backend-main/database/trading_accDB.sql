CREATE DATABASE IF NOT EXISTS `trading_accDB` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `trading_accDB`;

# TRADING_ACCDB
DROP TABLE IF EXISTS `trading_acc`;
CREATE TABLE IF NOT EXISTS `trading_acc` (
  `trade_accid` INT NOT NULL AUTO_INCREMENT,
  `accid` INT NOT NULL,
  `trade_acc_balance` DECIMAL(13, 2) NOT NULL,
  `currency` CHAR(3) NOT NULL,
  PRIMARY KEY (`trade_accid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO `trading_acc` (`trade_accid`, `accid`, `trade_acc_balance`, `currency`) VALUES
('4000001', '1000001', '1000.00', 'USD'),
('4000002', '1000002', '500.00', 'USD');
COMMIT;

select * from trading_accDB.trading_acc;