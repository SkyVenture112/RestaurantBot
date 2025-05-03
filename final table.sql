-- MySQL dump 10.13  Distrib 9.3.0, for macos14.7 (arm64)
--
-- Host: 127.0.0.1    Database: menu
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `CustomerTable`
--

DROP TABLE IF EXISTS `CustomerTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CustomerTable` (
  `customerID` int NOT NULL,
  `Name` varchar(100) DEFAULT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`customerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CustomerTable`
--

LOCK TABLES `CustomerTable` WRITE;
/*!40000 ALTER TABLE `CustomerTable` DISABLE KEYS */;
INSERT INTO `CustomerTable` VALUES (1,'Asher Maes','714-321-1241'),(2,'Tyler Hughes','714-124-4312'),(3,'Jerry Smith','714-121-1911'),(4,'John Cena','714-812-1241'),(5,'Barry Moore','714-813-1311'),(7,'Random Customer','N/A'),(8,'DiscordUser_334380770124627979','N/A'),(9,'DiscordUser_195227216689364993','N/A');
/*!40000 ALTER TABLE `CustomerTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MenuTable`
--

DROP TABLE IF EXISTS `MenuTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MenuTable` (
  `itemID` int NOT NULL,
  `Name` varchar(100) DEFAULT NULL,
  `Price` decimal(5,2) DEFAULT NULL,
  `isAvailable` tinyint(1) DEFAULT NULL,
  `Category` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`itemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MenuTable`
--

LOCK TABLES `MenuTable` WRITE;
/*!40000 ALTER TABLE `MenuTable` DISABLE KEYS */;
INSERT INTO `MenuTable` VALUES (1,'Bistro Sandwich',14.00,1,'Sandwich'),(2,'Brie LT',14.00,1,'Sandwich'),(3,'Our Turkey Club',14.00,0,'Sandwich'),(4,'Super Missile',14.00,1,'Hot Specialty'),(5,'California Crab Cake Sandwich',10.75,1,'Seafood Sandwich'),(6,'Ham and Swiss Melt',14.00,1,'Melt'),(7,'Spinach Melt',14.00,1,'Melt'),(8,'Caprese',14.00,1,'Vegetarian Sandwich'),(9,'Caprese Melt',14.00,1,'Vegetarian Melt'),(10,'Smoked Salmon Sandwich',18.00,1,'Seafood Sandwich'),(11,'Mom\'s Choice Grilled Cheese',12.00,1,'Grilled Cheese'),(12,'Gramma\'s Secret Grilled Cheese',12.00,1,'Grilled Cheese'),(13,'Special Cheeser Grilled Cheese',14.00,1,'Grilled Cheese'),(14,'Gourmet Grilled Cheese',15.00,1,'Grilled Cheese'),(15,'Hot Stuff Grilled Cheese',14.00,1,'Grilled Cheese'),(16,'Very Berry Salad',15.00,1,'Salad'),(17,'Chicken Caesar Salad',15.00,1,'Salad'),(18,'Ruth\'s Cobb Salad',15.00,1,'Salad'),(19,'Salmon Avocado Salad',18.00,1,'Seafood Salad'),(20,'Mixed Greens Salad',12.00,1,'Salad');
/*!40000 ALTER TABLE `MenuTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OrderDetailsTable`
--

DROP TABLE IF EXISTS `OrderDetailsTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OrderDetailsTable` (
  `orderID` int NOT NULL,
  `itemID` int NOT NULL,
  `Quantity` int DEFAULT NULL,
  `priceAtOrder` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`orderID`,`itemID`),
  KEY `itemID` (`itemID`),
  CONSTRAINT `orderdetailstable_ibfk_1` FOREIGN KEY (`orderID`) REFERENCES `OrderTable` (`orderID`),
  CONSTRAINT `orderdetailstable_ibfk_2` FOREIGN KEY (`itemID`) REFERENCES `MenuTable` (`itemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OrderDetailsTable`
--

LOCK TABLES `OrderDetailsTable` WRITE;
/*!40000 ALTER TABLE `OrderDetailsTable` DISABLE KEYS */;
INSERT INTO `OrderDetailsTable` VALUES (1,1,5,NULL),(1,2,2,NULL),(2,3,1,NULL),(2,4,3,NULL),(5,5,2,NULL),(6,2,1,NULL),(10,4,1,NULL),(11,3,1,542.00),(12,3,1,234.00),(13,3,1,999.00),(14,1,1,36.00),(15,3,1,28.00);
/*!40000 ALTER TABLE `OrderDetailsTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderTable`
--

DROP TABLE IF EXISTS `orderTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderTable` (
  `orderID` int NOT NULL,
  `orderDate` date DEFAULT NULL,
  `customerID` int DEFAULT NULL,
  `Status` enum('Fulfilled','Unfulfilled') DEFAULT NULL,
  `totalAmount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`orderID`),
  KEY `customerID` (`customerID`),
  CONSTRAINT `ordertable_ibfk_1` FOREIGN KEY (`customerID`) REFERENCES `CustomerTable` (`customerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderTable`
--

LOCK TABLES `orderTable` WRITE;
/*!40000 ALTER TABLE `orderTable` DISABLE KEYS */;
INSERT INTO `orderTable` VALUES (1,'2024-11-02',1,'Fulfilled',98.00),(2,'2024-11-03',1,'Fulfilled',56.00),(3,'2024-12-15',2,'Unfulfilled',8.99),(4,'2025-02-03',3,'Fulfilled',50.99),(5,'2025-04-16',4,'Fulfilled',21.50),(6,'2025-04-28',8,'Unfulfilled',14.00),(7,'2025-04-29',8,'Unfulfilled',0.00),(8,'2025-04-29',8,'Unfulfilled',0.00),(9,'2025-04-29',8,'Unfulfilled',0.00),(10,'2025-04-29',8,'Unfulfilled',14.00),(11,'2025-04-29',8,'Unfulfilled',14.00),(12,'2025-04-29',8,'Unfulfilled',14.00),(13,'2025-04-29',8,'Unfulfilled',14.00),(14,'2025-04-29',8,'Unfulfilled',14.00),(15,'2025-04-29',8,'Unfulfilled',14.00);
/*!40000 ALTER TABLE `orderTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RatingTable`
--

DROP TABLE IF EXISTS `RatingTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RatingTable` (
  `ratingID` int NOT NULL,
  `customerID` int DEFAULT NULL,
  `Rating` decimal(2,1) DEFAULT NULL,
  `Comment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ratingID`),
  KEY `customerID` (`customerID`),
  CONSTRAINT `ratingtable_ibfk_1` FOREIGN KEY (`customerID`) REFERENCES `CustomerTable` (`customerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RatingTable`
--

LOCK TABLES `RatingTable` WRITE;
/*!40000 ALTER TABLE `RatingTable` DISABLE KEYS */;
INSERT INTO `RatingTable` VALUES (1,1,3.5,'Not bad'),(2,2,4.5,'Great'),(3,3,4.0,'Awesome'),(4,4,4.0,'Amazing'),(5,5,5.0,'Perfect');
/*!40000 ALTER TABLE `RatingTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ReservationTable`
--

DROP TABLE IF EXISTS `ReservationTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ReservationTable` (
  `reservationID` int NOT NULL,
  `reservationDate` date DEFAULT NULL,
  `customerID` int DEFAULT NULL,
  `time` time DEFAULT NULL,
  PRIMARY KEY (`reservationID`),
  KEY `customerID` (`customerID`),
  CONSTRAINT `reservationtable_ibfk_1` FOREIGN KEY (`customerID`) REFERENCES `CustomerTable` (`customerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ReservationTable`
--

LOCK TABLES `ReservationTable` WRITE;
/*!40000 ALTER TABLE `ReservationTable` DISABLE KEYS */;
INSERT INTO `ReservationTable` VALUES (1,'2024-11-02',1,'03:54:51'),(2,'2024-11-03',2,'01:54:48'),(3,'2024-12-15',3,'02:54:45'),(4,'2025-02-03',4,'03:54:42'),(5,'2025-04-16',5,'15:54:38');
/*!40000 ALTER TABLE `ReservationTable` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-03 12:54:23
