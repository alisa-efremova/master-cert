import re
import uuid
from iso3166 import countries
from iso4217 import Currency

TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Request version="1.0">
  <Transaction mode="TEST" requestTimestamp="${timestamp(purchaseDate)}">
    <Identification>
      <ShortID>1111.2222.3333</ShortID>
      <UUID>${UUID}</UUID>
    </Identification>
    <MerchantAccount type="ACI_3DS_2">
      <ThreeDSecure fallback="false">
        <ThreeDSystem type="MasterCardSecureCode_v2">
          <AcquirerBIN>${acquirerBIN}</AcquirerBIN>
          <MerchantID>${threeDSRequestorID}</MerchantID>
          <MerchantName>${threeDSRequestorName}</MerchantName>
        </ThreeDSystem>
        <MerchantName>${merchantName}</MerchantName>
        <MerchantUrl>${threeDSRequestorURL}</MerchantUrl>
        <MerchantCountry>${merchantCountryCode}</MerchantCountry>
        <MerchantId>${acquirerMerchantID}</MerchantId>
        <MerchantCategory>${mcc}</MerchantCategory>
      </ThreeDSecure>
    </MerchantAccount>
    <Payment previousAmount="0.00" type="TD">
      <Amount>${amount(purchaseAmount)}</Amount>
      <Currency>${iso4217(purchaseCurrency)}</Currency>
    </Payment>
    <CreditCardAccount>
      <Holder>${cardholderName}</Holder>
      <Verification>123</Verification>
      <Brand>MASTER</Brand>
      <Number>${acctNumber}</Number>
      <Expiry month="${month(cardExpiryDate)}" year="${year(cardExpiryDate)}"/>
    </CreditCardAccount>
    <Customer>
      <Contact>
        <Email>${email}</Email>
        <Phone>${phone(homePhone)}</Phone>
        <Mobile>${phone(mobilePhone)}</Mobile>
      </Contact>
      <Address>
        <Street>${billAddrLine1}</Street>
        <Zip>${billAddrPostCode}</Zip>
        <City>${billAddrCity}</City>
        <State>${billAddrState}</State>
        <Country>${iso3166(billAddrCountry)}</Country>
      </Address>
    </Customer>
    <Parameters>
      <Parameter name="OPP_billing.street2">${billAddrLine2}</Parameter>
      <Parameter name="OPP_shipping.city">${shipAddrCity}</Parameter>
      <Parameter name="OPP_shipping.country">${iso3166(shipAddrCountry)}</Parameter>
      <Parameter name="OPP_shipping.street1">${shipAddrLine1}</Parameter>
      <Parameter name="OPP_shipping.street2">${shipAddrLine2}</Parameter>
      <Parameter name="OPP_shipping.postcode">${shipAddrPostCode}</Parameter>
      <Parameter name="OPP_shipping.state">${shipAddrState}</Parameter>
      <Parameter name="MODEL_customer.workPhone">${phone(workPhone)}</Parameter>
      <Parameter name="MODEL_customer.browser.acceptHeader">${browserAcceptHeader}</Parameter>
      <Parameter name="MODEL_customer.browser.language">${browserLanguage}</Parameter>
      <Parameter name="MODEL_customer.browser.screenHeight">${browserScreenHeight}</Parameter>
      <Parameter name="MODEL_customer.browser.screenWidth">${browserScreenWidth}</Parameter>
      <Parameter name="MODEL_customer.browser.timezone">${browserTZ}</Parameter>
      <Parameter name="MODEL_customer.browser.userAgent">${browserUserAgent}</Parameter>
      <Parameter name="MODEL_customer.browser.ipAddress">${browserIP}</Parameter>
      <Parameter name="MODEL_customer.browser.javaEnabled">${browserJavaEnabled}</Parameter>
      <Parameter name="MODEL_customer.browser.screenColorDepth">${browserColorDepth}</Parameter>
      <Parameter name="ReqAuthMethod">${threeDSRequestorAuthenticationInfo.threeDSReqAuthMethod}</Parameter>
      <Parameter name="ReqAuthTimestamp">${threeDSRequestorAuthenticationInfo.threeDSReqAuthTimestamp}</Parameter>
      <Parameter name="AccountId">${acctID}</Parameter>
      <Parameter name="AccountAgeIndicator">${acctInfo.chAccAgeInd}</Parameter>
      <Parameter name="AccountChangeDate">${acctInfo.chAccChange}</Parameter>
      <Parameter name="AccountChangeIndicator">${acctInfo.chAccChangeInd}</Parameter>
      <Parameter name="AccountDate">${acctInfo.chAccDate}</Parameter>
      <Parameter name="AccountPasswordChangeDate">${acctInfo.chAccPwChange}</Parameter>
      <Parameter name="AccountPasswordChangeIndicator">${acctInfo.chAccPwChangeInd}</Parameter>
      <Parameter name="AccountPurchaseCount">${acctInfo.nbPurchaseAccount}</Parameter>
      <Parameter name="AccountProvisioningAttempts">${acctInfo.provisionAttemptsDay}</Parameter>
      <Parameter name="AccountDayTransactions">${acctInfo.txnActivityDay}</Parameter>
      <Parameter name="AccountYearTransactions">${acctInfo.txnActivityYear}</Parameter>
      <Parameter name="PaymentAccountAge">${acctInfo.paymentAccAge}</Parameter>
      <Parameter name="PaymentAccountAgeIndicator">${acctInfo.paymentAccInd}</Parameter>
      <Parameter name="ShipAddressUsageDate">${acctInfo.shipAddressUsage}</Parameter>
      <Parameter name="ShipAddressUsageIndicator">${acctInfo.shipAddressUsageInd}</Parameter>
      <Parameter name="ShipIndicator">${merchantRiskIndicator.shipIndicator}</Parameter>
      <Parameter name="ShipNameIndicator">${acctInfo.shipNameIndicator}</Parameter>
      <Parameter name="SuspiciousAccountActivity">${acctInfo.suspiciousAccActivity}</Parameter>
      <Parameter name="RequestorChallengeInd">${threeDSRequestorChallengeInd}</Parameter>
      <Parameter name="USE_3D_SIMULATOR">FALSE</Parameter>
      ${MOBILE_PARAM}
    </Parameters>
  </Transaction>
</Request>"""

MOBILE_PARAM_TEMPLATE = """<Parameter name="OPP_threeDSecure.deviceInfo">{"messageType":"AuthRequest","messageVersion":"${messageVersion}","deviceChannel":"${deviceChannel}","sdkTransID":"${sdkTransID}","sdkAppID":"${sdkAppID}","sdkReferenceNumber":"${sdkReferenceNumber}","sdkEphemPubKey":"${sdkEphemPubKey}","sdkEncData":"${sdkEncData}","sdkMaxTimeout":"${sdkMaxTimeout}","sdkInterface":"03","sdkUiType":"31"}</Parameter>"""

class RequestAdapter(object):
    __data = {}
    __defaultValue = " "

    def __init__(self, data):
        self.__data = data

    def adapt_request(self):
        request = re.sub("\\${([^}]*)}", self.resolve, TEMPLATE)
        print("Built request: " + request)
        return request

    def resolve(self, match):
        if len(match.groups()) == 0:
            raise Exception("Template is corrupt!")
        return str(self.resolve_arg(match.groups()[0]))

    def resolve_arg(self, target):
        try:
            if target == "UUID":
                return str(uuid.uuid4()).replace("-", "")
            elif: target == "MOBILE_PARAM"
                return re.sub("\\${([^}]*)}", self.resolve, MOBILE_PARAM_TEMPLATE)
            else:
                match = re.fullmatch("([a-z0-9]+)\\(([^}]*)\\)", target)
                if match is not None:
                    fname = match.groups()[0]
                    arg = match.groups()[1]
                    if not hasattr(self, fname):
                        raise Exception("Processing method " + fname + "() is not defined!")
                    function = getattr(self, fname)
                    return function(self.resolve_arg(arg))
                else:
                    parent = self.__data
                    for ref in target.split("."):
                        parent = parent[ref]
                    return parent
        except Exception as e:
            print("[WARNING] Unable to substitute " + target + ", defaulting to " + self.__defaultValue)
            return self.__defaultValue

    def year(self, str):
        return "20" + str[:2]

    def month(self, str):
        return str[2:]

    def phone(self, obj):
       return obj["cc"] + "-" + obj["subscriber"]

    def timestamp(self, str):
        return str[:4] + "-" + str[4:6] + "-" + str[6:8] + " " + str[8:10] + ":" + str[10:12] + ":" + str[12:]

    def iso3166(self, num):
        return countries.get(num).alpha2

    def iso4217(self, str):
        return next(c for c in Currency if c.number == int(str)).code

    def amount(self, str):
        if "." in str:
            return str
        return str + ".00"
