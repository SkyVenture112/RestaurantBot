# Restaurant Bot
A Discord bot that utilizes a MySQL database to manage restaurant reservations.

## Authors
Tyler Momani (momani@chapman.edu) and Jack Dippel (dippel@chapman.edu)

## Source Files

* ``bot.py`` - main method
* ``user_commands.py`` - aggregation of all the user command implementations
* ``admin_commands.py`` - aggregation of all the administrator command implementations)
* ``menu.sql`` - database dump


## Features

Our Discord bot implements many of the features typically found in a MySQL database. Here is an non-exhaustive list:

* Displays records from database tables (``!view_menu``)
* Queries for data within the database tables using a variety of different parameters (``!popular_items``, which utilizes a limit to the amount of records it returns)
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


## Execution Instructions

Once the Discord bot has been invited to a server, it can be run by doing the following:

* Ensure a local version of MySQL is running by executing the command
``bash
mysql -u root -p
``

(It is also necessary to connect the menu database to LocalHost so that no errors arise.)

* Run the command
``bash
python bot.py
``





