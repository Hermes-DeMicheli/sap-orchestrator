managed implementation in class zbp_r_travel unique;
strict ( 2 );
with draft;

define behavior for ZR_Travel alias Travel
persistent table ztravel
draft table ztravel_d
etag master LocalLastChangedAt
lock master total etag LastChangedAt
authorization master ( global, instance )
{
  field ( readonly ) TravelUUID, LocalLastChangedAt, LastChangedAt;
  field ( numbering : managed ) TravelUUID;
  field ( mandatory ) AgencyID;

  create;
  update;
  delete;

  association _Booking { create; with draft; }

  action ( features : instance ) acceptTravel result [1] $self;
  validation validateAgency on save { create; field AgencyID; }
  determination setInitialStatus on modify { create; }

  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume;
  draft determine action Prepare { validation validateAgency; }

  mapping for ztravel corresponding
  {
    TravelUUID         = travel_uuid;
    TravelID           = travel_id;
    AgencyID           = agency_id;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}
