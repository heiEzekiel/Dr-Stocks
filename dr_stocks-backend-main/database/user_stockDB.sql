CREATE DATABASE IF NOT EXISTS `user_stockDB` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `user_stockDB`;

# USER_STOCKDB
DROP TABLE IF EXISTS `user_stock`;
CREATE TABLE IF NOT EXISTS `user_stock` (
  `user_stockid` INT NOT NULL AUTO_INCREMENT,
  `accid` INT NOT NULL,
  `tradeid` INT NOT NULL,
  `stock_symbol` CHAR(5) NOT NULL,
  `stock_quantity` INT NOT NULL,
  `purchased_price` DECIMAL(13, 2) NOT NULL,
  `currency` CHAR(3) NOT NULL,
  PRIMARY KEY (`user_stockid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `user_stock` (`user_stockid`, `accid`, `tradeid`,`stock_symbol`, `stock_quantity`, `purchased_price`, `currency`) VALUES
('5000001', '1000001', '4000001','AAPL', '1', '154.73', 'USD'),
('5000002', '1000002', '4000002','AMD', '1', '104.29', 'USD');
COMMIT;

select * from user_stockDB.user_stock;