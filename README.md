# Restaurant Bot
A Discord bot that manages restaurant reservations.

## Authors
Tyler Momani (momani@chapman.edu) and Jack Dippel (dippel@chapman.edu)

## Source Files

* bot2.py (main method)
* menu.sql (database dump)


## Features

Our Discord bot implements many of the features typically found in a MySQL database. Here is an non-exhaustive list:

* Displays records from the tables (``!view_menu``)
* Queries for data within the tables using a variety of different parameters (``!popular_items``, which utilizes a limit to the amount of records it returns)
* Creates new records (``!order``, ``!feedback``, ``!reserve``)
* Deletes records (``!cancel_order``)
* Updates records (``!mark_fulfilled``)
* Utilizes database transactions (``!order``)
* Generates exportable .csv reports (``!export_sales``)
* Contains queries that perform a group-by clause (``!popular_items``, ``!ratings_summary``)
* Contains queries that utilize subqueries (``!top_spender_on_expensive``)
* Contains queries that perform joins across multiple tables (``!full_order_history``)
* Enforces referential integrity by implementing primary and foreign keys
* Utilizes a database view (``!popular_items``)
* Utilizes multiple different entities (Customers, Orders, Reservations, Ratings, Menu Items)






