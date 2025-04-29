-- MySQL dump 10.13  Distrib 9.2.0, for Win64 (x86_64)
--
-- Host: localhost    Database: menu
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
-- Table structure for table `customertable`
--

DROP TABLE IF EXISTS `customertable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customertable` (
  `customerID` int NOT NULL,
  `Name` varchar(100) DEFAULT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`customerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customertable`
--

LOCK TABLES `customertable` WRITE;
/*!40000 ALTER TABLE `customertable` DISABLE KEYS */;
INSERT INTO `customertable` VALUES (1,'Asher Maes','714-321-1241'),(2,'Tyler Hughes','714-124-4312'),(3,'Jerry Smith','714-121-1911'),(4,'John Cena','714-812-1241'),(5,'Barry Moore','714-813-1311');
/*!40000 ALTER TABLE `customertable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menutable`
--

DROP TABLE IF EXISTS `menutable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menutable` (
  `itemID` int NOT NULL,
  `Name` varchar(100) DEFAULT NULL,
  `Price` decimal(5,2) DEFAULT NULL,
  `isAvailable` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`itemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menutable`
--

LOCK TABLES `menutable` WRITE;
/*!40000 ALTER TABLE `menutable` DISABLE KEYS */;
INSERT INTO `menutable` VALUES (1,'Bistro Sandwich',14.00,1),(2,'Brie LT',14.00,1),(3,'Our Turkey Club',14.00,1),(4,'Super Missile',14.00,1),(5,'California Crab Cake Sandwich',10.75,1),(6,'Ham and Swiss Melt',14.00,1),(7,'Spinach Melt',14.00,1),(8,'Caprese',14.00,1),(9,'Caprese Melt',14.00,1),(10,'Smoked Salmon Sandwich',18.00,1),(11,'Mom\'s Choice Grilled Cheese',12.00,1),(12,'Gramma\'s Secret Grilled Cheese',12.00,1),(13,'Special Cheeser Grilled Cheese',14.00,1),(14,'Gourmet Grilled Cheese',15.00,1),(15,'Hot Stuff Grilled Cheese',14.00,1),(16,'Very Berry Salad',15.00,1),(17,'Chicken Caesar Salad',15.00,1),(18,'Ruth\'s Cobb Salad',15.00,1),(19,'Salmon Avocado Salad',18.00,1),(20,'Mixed Greens Salad',12.00,1);
/*!40000 ALTER TABLE `menutable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderdetailstable`
--

DROP TABLE IF EXISTS `orderdetailstable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderdetailstable` (
  `orderID` int NOT NULL,
  `itemID` int NOT NULL,
  `Quantity` int DEFAULT NULL,
  PRIMARY KEY (`orderID`,`itemID`),
  KEY `itemID` (`itemID`),
  CONSTRAINT `orderdetailstable_ibfk_1` FOREIGN KEY (`orderID`) REFERENCES `ordertable` (`orderID`),
  CONSTRAINT `orderdetailstable_ibfk_2` FOREIGN KEY (`itemID`) REFERENCES `menutable` (`itemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderdetailstable`
--

LOCK TABLES `orderdetailstable` WRITE;
/*!40000 ALTER TABLE `orderdetailstable` DISABLE KEYS */;
INSERT INTO `orderdetailstable` VALUES (1,1,5),(1,2,2),(2,3,1),(2,4,3),(5,5,2);
/*!40000 ALTER TABLE `orderdetailstable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordertable`
--

DROP TABLE IF EXISTS `ordertable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordertable` (
  `orderID` int NOT NULL,
  `orderDate` date DEFAULT NULL,
  `customerID` int DEFAULT NULL,
  `Status` enum('Fulfilled','Unfulfilled') DEFAULT NULL,
  `totalAmount` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`orderID`),
  KEY `customerID` (`customerID`),
  CONSTRAINT `ordertable_ibfk_1` FOREIGN KEY (`customerID`) REFERENCES `customertable` (`customerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordertable`
--

LOCK TABLES `ordertable` WRITE;
/*!40000 ALTER TABLE `ordertable` DISABLE KEYS */;
INSERT INTO `ordertable` VALUES (1,'2024-11-02',1,'Fulfilled',9.99),(2,'2024-11-03',1,'Fulfilled',5.99),(3,'2024-12-15',2,'Unfulfilled',2.99),(4,'2025-02-03',3,'Fulfilled',3.99),(5,'2025-04-16',4,'Fulfilled',3.99);
/*!40000 ALTER TABLE `ordertable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratingtable`
--

DROP TABLE IF EXISTS `ratingtable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ratingtable` (
  `ratingID` int NOT NULL,
  `customerID` int DEFAULT NULL,
  `Rating` decimal(2,1) DEFAULT NULL,
  `Comment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ratingID`),
  KEY `customerID` (`customerID`),
  CONSTRAINT `ratingtable_ibfk_1` FOREIGN KEY (`customerID`) REFERENCES `customertable` (`customerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratingtable`
--

LOCK TABLES `ratingtable` WRITE;
/*!40000 ALTER TABLE `ratingtable` DISABLE KEYS */;
INSERT INTO `ratingtable` VALUES (1,1,3.5,'Not bad'),(2,2,4.5,'Great'),(3,3,4.0,'Awesome'),(4,4,4.0,'Amazing'),(5,5,5.0,'Perfect');
/*!40000 ALTER TABLE `ratingtable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservationtable`
--

DROP TABLE IF EXISTS `reservationtable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservationtable` (
  `reservationID` int NOT NULL,
  `reservationDate` date DEFAULT NULL,
  `customerID` int DEFAULT NULL,
  PRIMARY KEY (`reservationID`),
  KEY `customerID` (`customerID`),
  CONSTRAINT `reservationtable_ibfk_1` FOREIGN KEY (`customerID`) REFERENCES `customertable` (`customerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservationtable`
--

LOCK TABLES `reservationtable` WRITE;
/*!40000 ALTER TABLE `reservationtable` DISABLE KEYS */;
INSERT INTO `reservationtable` VALUES (1,'2024-11-02',1),(2,'2024-11-03',2),(3,'2024-12-15',3),(4,'2025-02-03',4),(5,'2025-04-16',5);
/*!40000 ALTER TABLE `reservationtable` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-28 21:18:18
