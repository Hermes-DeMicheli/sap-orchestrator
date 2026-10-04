@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true
@Search.searchable: true
@ObjectModel.semanticKey: [ 'TravelID' ]
define root view entity ZC_Travel
  provider contract transactional_query
  as projection on ZR_Travel
{
  key TravelUUID,
      @Search.defaultSearchElement: true
      TravelID,
      AgencyID,
      TotalPrice,
      CurrencyCode,
      OverallStatus,
      LocalLastChangedAt,
      _Booking : redirected to composition child ZC_Booking
}
