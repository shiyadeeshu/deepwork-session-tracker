# deepwork_sdk.SessionsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**complete_session**](SessionsApi.md#complete_session) | **PATCH** /sessions/{session_id}/complete | Complete a session (stores completion time)
[**create_session**](SessionsApi.md#create_session) | **POST** /sessions/ | Schedule a new work session
[**get_session**](SessionsApi.md#get_session) | **GET** /sessions/{session_id} | Get one session
[**get_session_history**](SessionsApi.md#get_session_history) | **GET** /sessions/history | Summary of past sessions: durations, pauses, completion ratio
[**list_sessions**](SessionsApi.md#list_sessions) | **GET** /sessions/ | List all sessions (newest first)
[**pause_session**](SessionsApi.md#pause_session) | **PATCH** /sessions/{session_id}/pause | Pause an active session and log the interruption reason
[**resume_session**](SessionsApi.md#resume_session) | **PATCH** /sessions/{session_id}/resume | Resume a paused session
[**start_session**](SessionsApi.md#start_session) | **PATCH** /sessions/{session_id}/start | Start a scheduled session


# **complete_session**
> SessionRead complete_session(session_id)

Complete a session (stores completion time)

Active → `completed` if finished within scheduled duration + 10%, else `overdue`. Paused (never resumed) → `abandoned`.

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_read import SessionRead
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
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_id = 56 # int | 

    try:
        # Complete a session (stores completion time)
        api_response = api_instance.complete_session(session_id)
        print("The response of SessionsApi->complete_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->complete_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **int**|  | 

### Return type

[**SessionRead**](SessionRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Session not found |  -  |
**409** | Action not allowed in the current status |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_session**
> SessionRead create_session(session_create)

Schedule a new work session

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_create import SessionCreate
from deepwork_sdk.models.session_read import SessionRead
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
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_create = deepwork_sdk.SessionCreate() # SessionCreate | 

    try:
        # Schedule a new work session
        api_response = api_instance.create_session(session_create)
        print("The response of SessionsApi->create_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->create_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_create** | [**SessionCreate**](SessionCreate.md)|  | 

### Return type

[**SessionRead**](SessionRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session**
> SessionRead get_session(session_id)

Get one session

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_read import SessionRead
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
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_id = 56 # int | 

    try:
        # Get one session
        api_response = api_instance.get_session(session_id)
        print("The response of SessionsApi->get_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->get_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **int**|  | 

### Return type

[**SessionRead**](SessionRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Session not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_history**
> HistorySummary get_session_history()

Summary of past sessions: durations, pauses, completion ratio

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.history_summary import HistorySummary
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
    api_instance = deepwork_sdk.SessionsApi(api_client)

    try:
        # Summary of past sessions: durations, pauses, completion ratio
        api_response = api_instance.get_session_history()
        print("The response of SessionsApi->get_session_history:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->get_session_history: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**HistorySummary**](HistorySummary.md)

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

# **list_sessions**
> List[SessionRead] list_sessions()

List all sessions (newest first)

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_read import SessionRead
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
    api_instance = deepwork_sdk.SessionsApi(api_client)

    try:
        # List all sessions (newest first)
        api_response = api_instance.list_sessions()
        print("The response of SessionsApi->list_sessions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->list_sessions: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[SessionRead]**](SessionRead.md)

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

# **pause_session**
> SessionRead pause_session(session_id, pause_request)

Pause an active session and log the interruption reason

Only active sessions can be paused. The 4th pause marks the session `interrupted`.

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.pause_request import PauseRequest
from deepwork_sdk.models.session_read import SessionRead
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
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_id = 56 # int | 
    pause_request = deepwork_sdk.PauseRequest() # PauseRequest | 

    try:
        # Pause an active session and log the interruption reason
        api_response = api_instance.pause_session(session_id, pause_request)
        print("The response of SessionsApi->pause_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->pause_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **int**|  | 
 **pause_request** | [**PauseRequest**](PauseRequest.md)|  | 

### Return type

[**SessionRead**](SessionRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Session not found |  -  |
**409** | Action not allowed in the current status |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resume_session**
> SessionRead resume_session(session_id)

Resume a paused session

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_read import SessionRead
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
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_id = 56 # int | 

    try:
        # Resume a paused session
        api_response = api_instance.resume_session(session_id)
        print("The response of SessionsApi->resume_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->resume_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **int**|  | 

### Return type

[**SessionRead**](SessionRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Session not found |  -  |
**409** | Action not allowed in the current status |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_session**
> SessionRead start_session(session_id)

Start a scheduled session

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_read import SessionRead
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
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_id = 56 # int | 

    try:
        # Start a scheduled session
        api_response = api_instance.start_session(session_id)
        print("The response of SessionsApi->start_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->start_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **int**|  | 

### Return type

[**SessionRead**](SessionRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Session not found |  -  |
**409** | Action not allowed in the current status |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

