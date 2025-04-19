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
INSERT INTO `CustomerTable` VALUES (1,'Asher Maes','714-321-1241'),(2,'Tyler Hughes','714-124-4312'),(3,'Jerry Smith','714-121-1911'),(4,'John Cena','714-812-1241'),(5,'Barry Moore','714-813-1311');
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
  PRIMARY KEY (`itemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MenuTable`
--

LOCK TABLES `MenuTable` WRITE;
/*!40000 ALTER TABLE `MenuTable` DISABLE KEYS */;
INSERT INTO `MenuTable` VALUES (1,'Bistro Sandwich',14.00,1),(2,'Brie LT',14.00,1),(3,'Our Turkey Club',14.00,1),(4,'Super Missile',14.00,1),(5,'California Crab Cake Sandwich',10.75,1),(6,'Ham and Swiss Melt',14.00,1),(7,'Spinach Melt',14.00,1),(8,'Caprese',14.00,1),(9,'Caprese Melt',14.00,1),(10,'Smoked Salmon Sandwich',18.00,1),(11,'Mom\'s Choice Grilled Cheese',12.00,1),(12,'Gramma\'s Secret Grilled Cheese',12.00,1),(13,'Special Cheeser Grilled Cheese',14.00,1),(14,'Gourmet Grilled Cheese',15.00,1),(15,'Hot Stuff Grilled Cheese',14.00,1),(16,'Very Berry Salad',15.00,1),(17,'Chicken Caesar Salad',15.00,1),(18,'Ruth\'s Cobb Salad',15.00,1),(19,'Salmon Avocado Salad',18.00,1),(20,'Mixed Greens Salad',12.00,1);
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
INSERT INTO `OrderDetailsTable` VALUES (1,1,5),(1,2,2),(2,3,1),(2,4,3),(5,5,2);
/*!40000 ALTER TABLE `OrderDetailsTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OrderTable`
--

DROP TABLE IF EXISTS `OrderTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OrderTable` (
  `orderID` int NOT NULL,
  `orderDate` date DEFAULT NULL,
  `customerID` int DEFAULT NULL,
  `Status` enum('Fulfilled','Unfulfilled') DEFAULT NULL,
  PRIMARY KEY (`orderID`),
  KEY `customerID` (`customerID`),
  CONSTRAINT `ordertable_ibfk_1` FOREIGN KEY (`customerID`) REFERENCES `CustomerTable` (`customerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OrderTable`
--

LOCK TABLES `OrderTable` WRITE;
/*!40000 ALTER TABLE `OrderTable` DISABLE KEYS */;
INSERT INTO `OrderTable` VALUES (1,'2024-11-02',1,'Fulfilled'),(2,'2024-11-03',1,'Fulfilled'),(3,'2024-12-15',2,'Unfulfilled'),(4,'2025-02-03',3,'Fulfilled'),(5,'2025-04-16',4,'Fulfilled');
/*!40000 ALTER TABLE `OrderTable` ENABLE KEYS */;
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
INSERT INTO `ReservationTable` VALUES (1,'2024-11-02',1),(2,'2024-11-03',2),(3,'2024-12-15',3),(4,'2025-02-03',4),(5,'2025-04-16',5);
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

-- Dump completed on 2025-04-19 14:36:41
