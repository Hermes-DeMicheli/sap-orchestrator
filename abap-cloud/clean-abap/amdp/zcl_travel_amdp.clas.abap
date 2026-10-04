CLASS zcl_travel_amdp DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_amdp_marker_hdb.
    TYPES tt_travel TYPE STANDARD TABLE OF ztravel WITH EMPTY KEY.
    CLASS-METHODS get_expensive_travels
      IMPORTING VALUE(iv_min_price) TYPE ztravel-total_price
      EXPORTING VALUE(et_travels)   TYPE tt_travel.
ENDCLASS.

CLASS zcl_travel_amdp IMPLEMENTATION.
  METHOD get_expensive_travels
    BY DATABASE PROCEDURE FOR HDB LANGUAGE SQLSCRIPT
    OPTIONS READ-ONLY
    USING ztravel.
    et_travels = SELECT * FROM ztravel
                 WHERE total_price >= :iv_min_price;
  ENDMETHOD.
ENDCLASS.
