@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Travel - Root BO'
define root view entity ZR_Travel
  as select from ztravel
  composition [0..*] of ZR_Booking as _Booking
  association [0..1] to /DMO/I_Agency as _Agency on $projection.AgencyID = _Agency.AgencyID
{
  key travel_uuid           as TravelUUID,
      travel_id             as TravelID,
      agency_id             as AgencyID,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      total_price           as TotalPrice,
      currency_code         as CurrencyCode,
      overall_status        as OverallStatus,
      @Semantics.user.createdBy: true
      local_created_by      as LocalCreatedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true
      last_changed_at       as LastChangedAt,
      _Booking,
      _Agency
}
