CREATE DATABASE IF NOT EXISTS `stock_prefDB` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `stock_prefDB`;

# STOCK_PREFDB
DROP TABLE IF EXISTS `stock_pref`;
CREATE TABLE IF NOT EXISTS `stock_pref` (
  `stock_prefid` INT NOT NULL AUTO_INCREMENT,
  `accid` INT NOT NULL,
  `stock_industry` CHAR(100) NOT NULL,
  PRIMARY KEY (`stock_prefid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `stock_pref` (`stock_prefid`, `accid`, `stock_industry`) VALUES
('3000001', '1000001', 'Energy'),
('3000002', '1000001', 'Information Technology'),
('3000003', '1000001', 'Financials'),
('3000004', '1000002', 'Real Estate'),
('3000005', '1000002', 'Materials');
COMMIT;

select * from stock_prefDB.stock_pref;