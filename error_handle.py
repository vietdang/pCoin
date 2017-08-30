

class ERROR:
	CONNECTION_FAIL          = -1	#Bittrex api JSON cannot connect to server
	CMD_UNSUCCESS            = -2	#Bittrex api JSON return "success"=False
	CMD_INVALID              = -3	#Bittrex api not supported. Ex: wrong market name.
	TIME_OUT                 = -4	#A cmd cannot be completed within a specific time.
	PARAMETERS_INVALID       = -5	#Inputs for api are invalid. Ex: "INSUFFICIENT_FUNDS"
