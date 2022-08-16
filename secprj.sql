CREATE DATABASE  IF NOT EXISTS `secprj` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `secprj`;
-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: secprj
-- ------------------------------------------------------
-- Server version	8.0.28

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity`
--

DROP TABLE IF EXISTS `activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity` (
  `activityid` varchar(100) NOT NULL,
  `user_id` varchar(8) NOT NULL,
  `severity` varchar(45) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `description` varchar(45) NOT NULL,
  PRIMARY KEY (`activityid`),
  KEY `user_idfkuser_id_idx` (`user_id`),
  CONSTRAINT `user_idfkuser_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity`
--

LOCK TABLES `activity` WRITE;
/*!40000 ALTER TABLE `activity` DISABLE KEYS */;
/*!40000 ALTER TABLE `activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_card`
--

DROP TABLE IF EXISTS `credit_card`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_card` (
  `cc_id` varchar(100) NOT NULL,
  `cvv` varchar(3) NOT NULL,
  `exp_mm` int NOT NULL,
  `exp_yy` int NOT NULL,
  `cc_username` varchar(100) NOT NULL,
  `user_id` varchar(8) NOT NULL,
  `card_id` varchar(45) NOT NULL,
  `en_cc_id` varchar(100) NOT NULL,
  PRIMARY KEY (`cc_id`,`user_id`,`card_id`),
  UNIQUE KEY `cc_id_UNIQUE` (`cc_id`),
  UNIQUE KEY `en_cc_id_UNIQUE` (`en_cc_id`),
  KEY `user_credit_id_idx` (`user_id`),
  CONSTRAINT `user_credit_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_card`
--

LOCK TABLES `credit_card` WRITE;
/*!40000 ALTER TABLE `credit_card` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_card` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS `order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order` (
  `order_id` varchar(8) NOT NULL,
  `user_id` varchar(8) NOT NULL,
  `product_id` varchar(45) NOT NULL,
  `quantity` int NOT NULL,
  `date_order` varchar(45) NOT NULL,
  PRIMARY KEY (`order_id`),
  KEY `order_user_id_idx` (`user_id`),
  KEY `order_product_id_idx` (`product_id`),
  CONSTRAINT `order_product_id` FOREIGN KEY (`product_id`) REFERENCES `product` (`product_id`),
  CONSTRAINT `order_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order`
--

LOCK TABLES `order` WRITE;
/*!40000 ALTER TABLE `order` DISABLE KEYS */;
/*!40000 ALTER TABLE `order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `otp_method`
--

DROP TABLE IF EXISTS `otp_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `otp_method` (
  `otp_id` int NOT NULL,
  `otp_desc` varchar(45) NOT NULL,
  PRIMARY KEY (`otp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `otp_method`
--

LOCK TABLES `otp_method` WRITE;
/*!40000 ALTER TABLE `otp_method` DISABLE KEYS */;
INSERT INTO `otp_method` VALUES (1,'authenticator'),(2,'email');
/*!40000 ALTER TABLE `otp_method` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `product_id` varchar(8) NOT NULL,
  `product_name` varchar(45) NOT NULL,
  `product_desc` varchar(45) NOT NULL,
  `product_price` decimal(10,2) NOT NULL,
  `product_stock` int NOT NULL,
  `product_status` varchar(8) NOT NULL,
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product`
--

LOCK TABLES `product` WRITE;
/*!40000 ALTER TABLE `product` DISABLE KEYS */;
/*!40000 ALTER TABLE `product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` varchar(8) NOT NULL,
  `username` varchar(45) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(45) NOT NULL,
  `status` varchar(45) NOT NULL DEFAULT 'customer',
  `role` varchar(45) DEFAULT NULL,
  `cart` varchar(1000) NOT NULL DEFAULT '{}',
  `f_counter` int NOT NULL DEFAULT '0',
  `f_strike` int NOT NULL DEFAULT '0',
  `lockout_expiry` varchar(45) DEFAULT NULL,
  `verification_status` varchar(5) NOT NULL DEFAULT 'False',
  `token` varchar(100) DEFAULT NULL,
  `VirtualDevice_ID` varchar(32) NOT NULL DEFAULT '',
  `Device_ID` varchar(1000) NOT NULL DEFAULT '',
  `Activation` varchar(45) DEFAULT 'yes',
  `Preferred` int DEFAULT NULL,
  `Question` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_otp`
--

DROP TABLE IF EXISTS `user_otp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_otp` (
  `user_id` varchar(8) NOT NULL,
  `otp_id` int NOT NULL,
  `secret` varchar(32) NOT NULL,
  `expiry_time` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`user_id`,`otp_id`),
  KEY `fk_otp_id_idx` (`otp_id`),
  CONSTRAINT `user_otpfk_otp_id` FOREIGN KEY (`otp_id`) REFERENCES `otp_method` (`otp_id`),
  CONSTRAINT `user_otpfk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_otp`
--

LOCK TABLES `user_otp` WRITE;
/*!40000 ALTER TABLE `user_otp` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_otp` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-08-15 22:14:08
