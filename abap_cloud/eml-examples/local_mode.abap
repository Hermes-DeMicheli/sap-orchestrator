" Dentro il behavior pool: IN LOCAL MODE salta authorization e feature control
METHOD acceptTravel.
  MODIFY ENTITIES OF zr_travel IN LOCAL MODE
    ENTITY Travel
      UPDATE FIELDS ( OverallStatus )
      WITH VALUE #( FOR key IN keys ( %tky = key-%tky  OverallStatus = 'A' ) )
    FAILED   failed
    REPORTED reported.

  READ ENTITIES OF zr_travel IN LOCAL MODE
    ENTITY Travel ALL FIELDS WITH CORRESPONDING #( keys )
    RESULT FINAL(travels).

  result = VALUE #( FOR travel IN travels ( %tky = travel-%tky  %param = travel ) ).
ENDMETHOD.
