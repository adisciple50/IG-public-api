'''
/*
 * Copyright (C) 2014 IG Group (webapisupport@ig.com)
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except Exception as  in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
'''
# Default API gateway
urlRoot = "https://demo-api.ig.com/gateway/deal"

url = window.location.href

# If deployed to a labs environment, override the default demo urlRoot
env = url.match("http:\/\/(.*)-labs.ig.com")

if env and env.length>1:
    envOverride = env[1].toLowerCase()
    urlRoot = urlRoot.replace("demo", envOverride)
	print("Overriding urlRoot with: " + urlRoot)
elif url.indexOf("localhost")>0:
    urlRoot = "https://web-api.ig.com/gateway/deal"
    print("Overriding urlRoot with: " + urlRoot)
}

# Globals variables
 accountId = None
 account_token = None
 client_token = None
 lsEndpoint = None
 lsClient
 ticketSubscription
 accountSubscription

require(["LightstreamerClient","Subscription"],function(LightstreamerClient,Subscription:

def getRequestParam(name){
   if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
      return decodeURIComponent(name[1])
}

/*
 * Function to connect to Lightstreamer
 */
def connectToLightstreamer():

      # Instantiate Lightstreamer client instance
      print("Connecting to Lighstreamer: " + lsEndpoint)
      lsClient = new LightstreamerClient(lsEndpoint)

      # Set up login credentials: client
      lsClient.connectionDetails.setUser(accountId)

       password = ""
      if client_token:
         password = "CST-" + client_token

      if client_token and account_token:
         password = password + "|"

      if account_token:
         password = password + "XST-" + account_token

      print(" LSS login " + accountId + " - " + password)
      lsClient.connectionDetails.setPassword(password)

      # Add connection event listener callback functions
      lsClient.addListener({
         onListenStart: def ():
            print('Lightstreamer client - start listening')
         ,
         onStatusChange: def (status):
            print('Lightstreamer connection status:' + status)

      })

      # Allowed bandwidth in kilobits/s
      //lsClient.connectionOptions.setMaxBandwidth()

      # Connect to Lightstreamer
      lsClient.connect()


def subscribeToLightstreamerTradeUpdates():
   # Create a Lightstreamer subscription for the BID and OFFER prices for the relevant market

      # Set up the Lightstreamer FIDs
      accountSubscription = new Subscription(
         "DISTINCT",
         "TRADE:" + accountId,
         [
            "CONFIRMS",
            "OPU",
            "WOU"
         ]
      )

      accountSubscription.setRequestedMaxFrequency("unfiltered")

      # Set up the Lightstreamer event listeners
      accountSubscription.addListener({
         onSubscription: def ():
            print('trade updates subscription succeeded')
         ,
         onSubscriptionError: def (code, message):
            print('trade updates subscription failure: ' + code + " message: " + message)
         ,
         onItemUpdate: def (updateInfo):

            print("received trade update message: " + updateInfo.getItemName())

            updateInfo.forEachField(def (fieldName, fieldPos, value):
               if value not = 'INV':
                  print("field: " + fieldName + " - value: " + value)
                  if fieldName == "CONFIRMS":
                     showDealConfirmDialog(value)
                  else:
                     showAccountStatusUpdate(value)


            )
         ,
         onItemLostUpdates: def ():
            print("trade updates subscription - item lost")


      })

      # Subscribe to Lightstreamer
      lsClient.subscribe(accountSubscription)

'''
/*
 * User interface login button callback function
 */
'''
def login():

   # Get username and password from user interface fields
   apiKey = $("#apikey").val()
    identifier = $("#username").val()
    password = $("#password").val()

   if apiKey=="" or identifier=="" or password=="":
       return False


   password = encryptedPassword(password)
   print("Encrypted password " + password)

   # Create a login request, ie a POST request to /session
    req = new Request()
   req.method = "POST"
   req.url = urlRoot + "/session"

   # Set up standard request headers, i.e. the api key, the request content type (JSON),
   # and the expected response content type (JSON)
   req.headers = {
      "Content-Type": "application/json; charset=UTF-8",
      "Accept": "application/json; charset=UTF-8",
      "X-IG-API-KEY": apiKey,
      "Version": "2"
   }

   # Set up the request body with the user identifier (username) and password
    bodyParams = {}
   bodyParams["identifier"] = identifier
   bodyParams["password"] = password
   bodyParams["encryptedPassword"] = True
   req.body = JSON.stringify(bodyParams)

   # Prettify the request for display purposes only
   $("#request_data").text(js_beautify(req.body) or "")

   # Send the request via a Javascript AJAX call
   try:
      $.ajax({
         type: req.method,
         url: req.url,
         data: req.body,
         headers: req.headers,
         async: False,
         mimeType: req.binary ? 'text/plain; charset=x-user-defined' : None,
         success: def (response, status, data):

            # Successful login
            # Extract account and client session tokens, active account id, and the Lightstreamer endpoint,
            # as these will be required for subsequent requests
            account_token = data.getResponseHeader("X-SECURITY-TOKEN")
            print("X-SECURITY-TOKEN: " + account_token)
            client_token = data.getResponseHeader("CST")
            print("CST: " + client_token)
            accountId = response.currentAccountId
            lsEndpoint = response.lightstreamerEndpoint

            # Prettify response for display purposes only
            $("#response_data").text(js_beautify(data.responseText) or "")

            # Show logged in status message on screen
            $("#loginStatus").css("color", "green").text("Logged in as " + accountId)
         ,
         error: def (response, status, error):

            # Login failed, usually because the login id and password aren't correct
            handleHTTPError(response)

      })
   except Exception as e:
      handleException(e)


    return True



""""
 * Encryption function
"""

def encryptedPassword(password):

     key = encryptionKey()

     asn, tree,
    rsa = new pidCrypt.RSA(),
    decodedKey = pidCryptUtil.decodeBase64(key.encryptionKey)

    asn = pidCrypt.ASN1.decode(pidCryptUtil.toByteArray(decodedKey))
    tree = asn.toHexTree()

    rsa.setPublicKeyFromASN(tree)

    return pidCryptUtil.encodeBase64(pidCryptUtil.convertFromHex(rsa.encrypt(password += '|' + key.timeStamp)))



""""
 * Encryption key getter function
"""
def encryptionKey():

         apiKey = $("#apikey").val()

        # Set up the request as a GET request to the address /session/encryptionkey
         req = new Request()
        req.method = "GET"
        req.url = urlRoot + "/session/encryptionKey"

        # Set up the request headers, i.e. the api key, the account security session token, the client security token,
        # the request content type (JSON), and the expected response content type (JSON)
        req.headers = {
            "X-IG-API-KEY": apiKey,
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json; charset=UTF-8"
        }

        # No body is required, as this is a GET request
        req.body = ""
        $("#request_data").text(js_beautify(req.body) or "")

        # Send the request via a Javascript AJAX call
         key
        try:
            $.ajax({
                type: req.method,
                url: req.url,
                data: req.body,
                headers: req.headers,
                async: False,
                mimeType: req.binary ? 'text/plain; charset=x-user-defined' : None,
                error: def (response, status, error):
                    handleHTTPError(response)
                ,
                success: def (response, status, data):

                    print("Encryption key retrieved ")
                    key = response

            })
        except Exception as e:

            # Failed to get the encryption key
            handleException(e)


        return key



/*
 * Function to retrieve the deal confirmation for the given deal reference
 */
def retrieveConfirm(dealReference):

   # Set up the request as a GET request to the address /confirms
    req = new Request()
   req.method = "GET"
   req.url = urlRoot + "/confirms/" + dealReference

   # Set up the request headers, i.e. the api key, the account security session token, the client security token,
   # the request content type (JSON), and the expected response content type (JSON)
   req.headers = {
      "X-IG-API-KEY": apiKey,
      "X-SECURITY-TOKEN": account_token,
      "CST": client_token,
      "Content-Type": "application/json; charset=UTF-8",
      "Accept": "application/json; charset=UTF-8"
   }

   # No body is required, as this is a GET request
   req.body = ""
   $("#request_data").text(js_beautify(req.body) or "")

   # Send the request via a Javascript AJAX call
    message
   try:
      $.ajax({
         type: req.method,
         url: req.url,
         data: req.body,
         headers: req.headers,
         async: False,
         mimeType: req.binary ? 'text/plain; charset=x-user-defined' : None,
         error: def (response, status, error):
            handleHTTPError(response)
         ,
         success: def (response, status, data):

            # Got confirm data back
            # Prettify response for display purposes only
            $("#response_data").text(js_beautify(data.responseText) or "")

            # Log and set the confirm for later display
            print("confirm retrieved")
            message = response

      })
   except Exception as e:

      # Failed to get the confirmation, possibly because the deal reference was not matched to any deal
      handleException(e)


   return message


/*
 * Function to retrieve the positions for the active account
 */
def positions():

   # Set up the request as a GET request to the address /positions
    req = new Request()
   req.method = "GET"
   req.url = urlRoot + "/positions"

   # Set up the request headers, i.e. the api key, the account security session token, the client security token,
   # the request content type (JSON), and the expected response content type (JSON)
   req.headers = {
      "X-IG-API-KEY": apiKey,
      "X-SECURITY-TOKEN": account_token,
      "CST": client_token,
      "Content-Type": "application/json; charset=UTF-8",
      "Accept": "application/json; charset=UTF-8"
   }

   # No body is required, as this is a GET request
   req.body = ""
   $("#request_data").text(js_beautify(req.body) or "")

   # Send the request via a Javascript AJAX call
   try:
      $.ajax({
         type: req.method,
         url: req.url,
         data: req.body,
         headers: req.headers,
         async: False,
         mimeType: req.binary ? 'text/plain; charset=x-user-defined' : None,
         error: def (response, status, error):
            # An unexpected error occurred
            handleHTTPError(response)
         ,
         success: def (response, status, data):

            # Position data was returned
            # Prettify the response for display purposes only
            $("#response_data").text(js_beautify(data.responseText) or "")

            # Log and display the retrieved positions, along with the Lightstreamer subscription FIDs for the BID and OFFER
            # price of each position's market
            $('#positions_list tbody').empty()
             epicsItems = []
            $(response.positions).each(def (index):
                positionData = response.positions[index]
                epic = positionData.market.epic
                canSubscribe = positionData.market.streamingPricesAvailable
                tidyEpic = epic.replace(/\./g, "_")
               $('#positions_list tbody:last')
                  .append($('<tr>')
                     .append($('<td>')
                        .append($('<img>')
                           .attr("class", tidyEpic + "_MARKET_STATE")))
                     .append($('<td>').append(positionData.market.instrumentName))
                     .append($('<td>').append(positionData.market.expiry))
                     .append($('<td>').append(positionData.position.direction + positionData.position.contractSize))
                     .append($('<td>')
                        .attr("id", tidyEpic + "_BID")
                        .append(positionData.market.bid))
                     .append($('<td>')
                        .attr("id", tidyEpic + "_OFFER")
                        .append(positionData.market.offer))
                  )

               if canSubscribe:
                   epicsItem = "L1:" + positionData.market.epic
                  epicsItems.append(epicsItem)
                  print("adding subscription index / item: " + index + " / " + epicsItem)

            )

            # Now subscribe to the BID and OFFER prices for each position market
            if epicsItems.length > 0:

                  # Set up Lightstreamer FIDs
                   subscription = new Subscription(
                     "MERGE",
                     epicsItems,
                     [
                        "BID",
                        "OFFER",
                        "MARKET_STATE"
                     ]
                  )

                  subscription.setRequestedSnapshot("yes")

                  # Set up Lightstreamer event listener
                  subscription.addListener({
                     onSubscription: def ():
                        print('subscribed')
                     ,
                     onSubscriptionError: def (code, message):
                        print('subscription failure: ' + code + " message: " + message)
                     ,
                     onItemUpdate: def (updateInfo):

                        # Lightstreamer published some data
                        # The item name in this case will be the market EPIC for which prices were subscribed to
                         epic = updateInfo.getItemName().split(":")[1]
                        updateInfo.forEachField(def (fieldName, fieldPos, value):
                            fieldId = epic.replace(/\./g, "_") + "_" + fieldName
                            cell = $("." + fieldId)

                           if fieldName == "MARKET_STATE":
                              //update status image
                              if value == "TRADEABLE":
                                 cell.attr("src", "assets/img/open.png")
                              elif value == "EDIT":
                                 cell.attr("src", "assets/img/edit.png")
                              else:
                                 cell.attr("src", "assets/img/close.png")

                           else:
                              if fieldName and cell:
                                 cell.empty()
                                 cell.append($('<div>').addClass("tickCell").toggle("highlight").append(value))


                        )

                  })

                  # Subscribe to Lightstreamer
                  lsClient.subscribe(subscription)



      })
   except Exception as e:
      handleException(e)



/*
 * Function to search for markets against which to trade
 */
def search():

   # Set up the request as a GET request to the address /markets with a search query parameter of ?searchterm={searchterm}
    searchTerm = $("#searchTerm").val()
    req = new Request()
   req.method = "GET"
   req.url = urlRoot + "/markets?searchTerm=" + searchTerm

   # Set up the request headers, i.e. the api key, the account security session token, the client security token,
   # the request content type (JSON), and the expected response content type (JSON)
   req.headers = {
      "X-IG-API-KEY": apiKey,
      "X-SECURITY-TOKEN": account_token,
      "CST": client_token,
      "Content-Type": "application/json; charset=UTF-8",
      "Accept": "application/json; charset=UTF-8"
   }

   # No body is required, as this is a GET request
   req.body = ""
   $("#request_data").text(js_beautify(req.body) or "")

   # Send the request via a Javascript AJAX call
   try:
      $.ajax({
         type: req.method,
         url: req.url,
         data: req.body,
         headers: req.headers,
         async: False,
         mimeType: req.binary ? 'text/plain; charset=x-user-defined' : None,
         error: def (response, status, error):
            # Something went wrong
            handleHTTPError(response)
         ,
         success: def (response, status, data):

            # A search result was returned
            # Prettify the response for display purposes only
            $("#response_data").text(js_beautify(data.responseText) or "")

            # Log and display the search results, along with the Lightstreamer subscription FIDs for the BID and OFFER
            # price of each market returned
            $('#search_results_list tbody').empty()
               epicsItems = []

            $(response.markets).each(def (index):
                marketsData = response.markets[index]
                epic = marketsData.epic
                canSubscribe = marketsData.streamingPricesAvailable
                tidyEpic = epic.replace(/\./g, "_")
                expiry = marketsData.expiry.replace(/ /g, "")
                linkId = "searchResult_" + tidyEpic

               $('#search_results_list tbody:last')
                  .append($('<tr>')
                     .append($('<td>')
                        .append($('<img>')
                           .attr("id", "search_" + tidyEpic + "_MARKET_STATE")))
                     .append(
                        $('<td>')
                           .append($('<a>')
                              .attr("id", linkId)
                              .append(marketsData.instrumentName))
                     )
                     .append($('<td>')
                        .append(expiry))
                     .append($('<td>')
                        .attr("id", "search_" + tidyEpic + "_BID")
                        .append(marketsData.bid))
                     .append($('<td>')
                        .attr("id", "search_" + tidyEpic + "_OFFER")
                        .append(marketsData.offer))
                  )

               $('#' + linkId).click(def ():
                  dealTicket(epic, expiry)
               )

               if canSubscribe:
                   epicsItem = "L1:" + marketsData.epic
                  epicsItems.append(epicsItem)


               return index < 39
            )

            # Now subscribe to the BID and OFFER prices for each market found
            if epicsItems.length > 0:

                  # Set up Lightstreamer FIDs
                   subscription = new Subscription(
                     "MERGE",
                     epicsItems,
                     [
                        "BID",
                        "OFFER",
                        "MARKET_STATE"
                     ]
                  )

                   subscription.setRequestedSnapshot("yes")

                  # Set up Lightstreamer event listener
                  subscription.addListener({
                     onSubscription: def ():
                        print('subscribed')
                     ,
                     onSubscriptionError: def (code, message):
                        print('subscription failure: ' + code + " message: " + message)
                     ,
                     onItemUpdate: def (updateInfo):

                        # Lightstreamer published some data
                        # The item name in this case will be the market EPIC for which prices were subscribed to
                         epic = updateInfo.getItemName().split(":")[1]
                         tidyEpic = epic.replace(/\./g, "_")
                        updateInfo.forEachField(def (fieldName, fieldPos, value):
                            fieldId = "search_" + tidyEpic + "_" + fieldName
                            cell = $("#" + fieldId)

                           if fieldName == "MARKET_STATE":
                              //update status image
                              if value == "TRADEABLE":
                                 cell.attr("src", "assets/img/open.png")
                              elif value == "EDIT":
                                 cell.attr("src", "assets/img/edit.png")
                              else:
                                 cell.attr("src", "assets/img/close.png")

                           else:
                              if fieldName and cell:
                                 cell.empty()
                                 cell.append($('<div>').addClass("tickCell").append(value).toggle("highlight"))


                        )

                  })

                  # Subscribe to Lightstreamer
                  lsClient.subscribe(subscription)



      })
   except Exception as e:
      handleException(e)



/*
 * Retrieve market details
 */
def marketDetails(epic):

   # Set up the request as a GET request to the address /markets with a path parameter of the market EPIC
    req = new Request()
   req.method = "GET"
   req.url = urlRoot + "/markets/" + epic

   # Set up the request headers, i.e. the api key, the account security session token, the client security token,
   # the request content type (JSON), and the expected response content type (JSON)
   req.headers = {
      "X-IG-API-KEY": apiKey,
      "X-SECURITY-TOKEN": account_token,
      "CST": client_token,
      "Content-Type": "application/json; charset=UTF-8",
      "Accept": "application/json; charset=UTF-8"
   }

   # No body is required, as this is a GET request
   req.body = ""
   $("#request_data").text(js_beautify(req.body) or "")

   # Send the request via a Javascript AJAX call
    resultData
   try:
      $.ajax({
         type: req.method,
         url: req.url,
         data: req.body,
         headers: req.headers,
         async: False,
         mimeType: req.binary ? 'text/plain; charset=x-user-defined' : None,
         error: def (response, status, error):
            # Something went wrong
            handleHTTPError(response)
         ,
         success: def (response, status, data):

            # Market details were returned
            # Prettify the response and store the result for later display
            $("#response_data").text(js_beautify(data.responseText) or "")
            print("market details retrieved")
            resultData = response

      })

   except Exception as e:
      handleException(e)

   return resultData


/*
 * Function to populate the deal trading ticket
 */
def dealTicket(epic, expiry):

   # Unsubscribe from any previous Lightstreamer subscriptions
   if ticketSubscription:
      lsClient.unsubscribe(ticketSubscription)


   # Get the EPIC of the market we want to trade against
   $('#trade_epic').val(epic)
   $('#trade_expiry').val(expiry)
    market = marketDetails(epic)
   $('#dealTicket_title').text('Deal Ticket - ' + market.instrument.name)

   # Set the buy and sell
   $('#ticket_buy_price').text(market.snapshot.offer)
   $('#ticket_sell_price').text(market.snapshot.bid)

   $('#trade_offer').val(market.snapshot.offer)
   $('#trade_bid').val(market.snapshot.bid)

   # Create a Lightstreamer subscription for the BID and OFFER prices for the relevant market

      # Set up the Lightstreamer FIDs
      ticketSubscription = new Subscription(
         "MERGE",
         "L1:" + epic,
         [
            "BID",
            "OFFER"
         ]
      )

     ticketSubscription.setRequestedSnapshot("yes")

      # Set up the Lightstreamer event listeners
      ticketSubscription.addListener({
         onSubscription: def ():
            print('subscribed')
         ,
         onSubscriptionError: def (code, message):
            print('subscription failure: ' + code + " message: " + message)
         ,
         onItemUpdate: def (updateInfo):

            # Lightstreamer notification received
            # Extract the BID and OFFER prices and display these
             epic = updateInfo.getItemName().split(":")[1]
             tidyEpic = epic.replace(/\./g, "_")
            updateInfo.forEachField(def (fieldName, fieldPos, value):
               if fieldName == "BID":
                  $('#ticket_sell_price').text(value)
                  $('#trade_bid').text(value)
               elif fieldName == "OFFER":
                  $('#ticket_buy_price').text(value)
                  $('#trade_offer').text(value)

            )

      })

      # Subscribe to Lightstreamer
      lsClient.subscribe(ticketSubscription)

   # Show deal ticket
   $('#dealTicket').modal('show')


/*
 * Function to create an OTC position
 */
def placeTrade():

   # Hide the deal ticket as it's no longer required
   $('#dealTicket').modal('hide')

   # Get the market, deal size, and direction from the deal ticket
   # TODO remove bid and offer from the API
    epic = $('#trade_epic').val()
    expiry = $('#trade_expiry').val()
    size = $('#trade_size').val()
    tradeBid = $('#trade_bid').val()
    tradeOffer = $('#trade_offer').val()
    direction = $('#trade_direction').val()

   # Create a POST request to /positions/otc
    req = new Request()
   req.method = "POST"
   req.url = urlRoot + "/positions/otc"

   # Set up the request headers, i.e. the api key, the account security session token, the client security token,
   # the request content type (JSON), and the expected response content type (JSON)
   req.headers = {
      "X-IG-API-KEY": apiKey,
      "X-SECURITY-TOKEN": account_token,
      "CST": client_token,
      "Content-Type": "application/json; charset=UTF-8",
      "Accept": "application/json; charset=UTF-8",
      "Version": "1"
   }

   # Set up the request body
    bodyParams = {}
   bodyParams["currencyCode"] = "GBP"
   bodyParams["epic"] = epic
   bodyParams["expiry"] = expiry
   bodyParams["direction"] = (direction == "+" ? "BUY" : "SELL")
   bodyParams["size"] = size
   bodyParams["forceOpen"] = False
   bodyParams["guaranteedStop"] = False
   bodyParams["orderType"] = "MARKET"

   req.body = JSON.stringify(bodyParams)

   # Prettify the request for display purposes only
   $("#request_data").text(js_beautify(req.body) or "")

   # Send the request via a Javascript AJAX call
    resultData
   try:
      $.ajax({
         type: req.method,
         url: req.url,
         data: req.body,
         headers: req.headers,
         async: False,
         mimeType: req.binary ? 'text/plain; charset=x-user-defined' : None,
         error: def (response, status, error):
            # Something went wrong
            handleHTTPError(response)
         ,
         success: def (response, status, data):
            # The order was created
            # Prettify and log the response
            $("#response_data").text(js_beautify(data.responseText) or "")
            print("order placed")
            resultData = response

      })
   except Exception as e:
      handleException(e)


   # If the deal was placed, wait for the deal confirmation
   if resultData:
      print(resultData)
      showDealInProgressDialog(resultData)


#   Note: this example relies on the Lightstreamer confirm, alternatively a client implementation might make use of the polling confirm service, illustrated below
#   setTimeout(function () {
#       message = retrieveConfirm(resultData.dealReference);
#      console.log(message);
#      $('#dealInProgress').modal("hide");
#      showDealConfirmDialog(message);
#   }, 1000);



/*
 * Function to display an in progress dialog for an order while we wait for its confirmation.
 */
def showDealInProgressDialog(resultData):
   $('#dealReference').text(resultData.dealReference)
   $('#dealInProgress').modal('show')



/*
 * Function to display the deal confirmation message and update the user interface positions list
 */
def showDealConfirmDialog(message):

   if message:
      $('#dealInProgress').modal('hide')
      print('confirm message: ' + message)

       confirm = JSON.parse(message)
      print('confirm - deal id: ' + confirm.dealId)
      print('confirm - json payload: ' + confirm)

      $('#dealId').text(confirm.dealId)
      $('#dealStatus').text(confirm.dealStatus)
      $('#dealConfirm').modal("show")

      # Refresh position list
      positions()




/*
 * Function to display an account update (WOU, OPU) message and update the positions list
 */
def showAccountStatusUpdate(message):
   if message:

       confirm = JSON.parse(message)
      print('Account update received: ' + confirm.dealId)
      print(confirm)




/*
 * Request object
 */
def Request(o):
   this.headers = {"Content-Type": "application/json; charset=UTF-8", "Accept": "application/json; charset=UTF-8"}
   this.body = ""
   this.method = ""
   this.url = ""


/*
 * Exception handler - displays details of the except Exception as ion on the screen
 */
def handleException(except Exception as ion:
   $("#response_data").text(except Exception as ion)
   $("#alertStatusCode").text("unknown")
   try:
       responseJson = jQuery.parseJSON(response.responseText)
      $("#alertErrorCode").text(responseJson.errorCode)
   except Exception as e:
      $("#alertErrorCode").text(except Exception as ion)
   }
   $("#errorAlert").show()
}

/*
 * Handle an HTTP error
 */
def handleHTTPError(response:
   $("#response_data").text(js_beautify(response.responseText))
   $("#alertStatusCode").text(response.status)
   try:
       responseJson = jQuery.parseJSON(response.responseText)
      $("#alertErrorCode").text(responseJson.errorCode)
   except Exception as e:
      $("#alertErrorCode").text(response.responseText)

   $("#errorAlert").show()
}


/*
 * User interface control functions
 */

$('#loginButton').click(def ():
   if login():
      connectToLightstreamer()
      subscribeToLightstreamerTradeUpdates()
      showTradingPane()

)

$('#positionsButton').click(def ():
   positions()
)

$('#searchButton').click(def ():
   search()
)

$('#place_trade_button').click(def ():
   placeTrade()
)

$('#erroralert-dismiss').click(def ():
   $('#errorAlert').hide()
)

$('#sell_button').click(def ():
   $('#sell_button').addClass("glowing-border-on")
   $('#sell_button').removeClass("glowing-border-off")
   $('#buy_button').addClass("glowing-border-off")
   $('#buy_button').removeClass("glowing-border-on")

   $('#trade_direction').val("-")
)

$('#buy_button').click(def ():
   $('#buy_button').addClass("glowing-border-on")
   $('#buy_button').removeClass("glowing-border-off")
   $('#sell_button').addClass("glowing-border-off")
   $('#sell_button').removeClass("glowing-border-on")

   $('#trade_direction').val("+")
)


def showTradingPane():
   $('#landing').addClass("container-hidden")
   $('#landing').removeClass("container")
   $('#container').removeClass("container-hidden")
   $('#container').addClass("container")

})
:
:
