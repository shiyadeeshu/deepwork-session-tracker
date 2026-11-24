# deepwork_sdk.HealthApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health_check**](HealthApi.md#health_check) | **GET** /health | Health


# **health_check**
> object health_check()

Health

### Example


```python
import deepwork_sdk
from deepwork_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = deepwork_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with deepwork_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = deepwork_sdk.HealthApi(api_client)

    try:
        # Health
        api_response = api_instance.health_check()
        print("The response of HealthApi->health_check:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->health_check: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

