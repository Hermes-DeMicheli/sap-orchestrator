" Consumer esterno al BO: MODIFY + COMMIT con gestione response
MODIFY ENTITIES OF zr_travel
  ENTITY Travel
    UPDATE FIELDS ( OverallStatus )
    WITH VALUE #( ( %tky = travel_key-%tky  OverallStatus = 'A' ) )
  FAILED   FINAL(failed_modify)
  REPORTED FINAL(reported_modify).

IF failed_modify IS INITIAL.
  COMMIT ENTITIES
    RESPONSE OF zr_travel
      FAILED   FINAL(failed_commit)
      REPORTED FINAL(reported_commit).
ELSE.
  ROLLBACK ENTITIES.
ENDIF.
