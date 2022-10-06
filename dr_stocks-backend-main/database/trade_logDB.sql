CREATE DATABASE IF NOT EXISTS `trade_logDB` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `trade_logDB`;

# TRADE_LOGEB
DROP TABLE IF EXISTS `trade_log`;
CREATE TABLE IF NOT EXISTS `trade_log` (
  `tradeid` INT NOT NULL AUTO_INCREMENT,
  `accid` INT NOT NULL,
  `trade_date` DATETIME NOT NULL,
  `trade_value` DECIMAL(13, 2) NOT NULL,
  `trade_stock_symbol` CHAR(5) NOT NULL,
  `trade_quantity` INT NOT NULL,
  `currency` CHAR(3) NOT NULL,
  `trade_action` VARCHAR(20) NOT NULL,
  `status` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`tradeid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `trade_log` (`tradeid`, `accid`, `trade_date`,`trade_value`, `trade_stock_symbol`, `trade_quantity`, `currency`, `trade_action`, `status`) VALUES
('6000001', '1000001', '2022-03-10 13:44:02','154.73', 'AAPL', '1', 'USD', 'BUY', 'SUCCESS'),
('6000002', '1000002', '2022-03-10 15:43:27','104.29', 'AMD', '1', 'USD', 'BUY', 'SUCCESS');
COMMIT;

select * from trade_logDB.trade_log;