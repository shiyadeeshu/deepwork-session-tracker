# HistorySummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_sessions** | **int** | All sessions, any status | 
**finished_sessions** | **int** | Sessions in a final state | 
**status_counts** | **Dict[str, int]** |  | 
**completion_ratio** | **float** | completed / finished sessions (0.0 when nothing has finished) | 
**total_pauses** | **int** |  | 
**average_pauses_per_session** | **float** |  | 
**total_focus_minutes** | **float** | Sum of actual durations of finished sessions | 
**average_duration_minutes** | **float** |  | 
**sessions** | [**List[SessionHistoryItem]**](SessionHistoryItem.md) | Finished sessions, newest first | 

## Example

```python
from deepwork_sdk.models.history_summary import HistorySummary

# TODO update the JSON string below
json = "{}"
# create an instance of HistorySummary from a JSON string
history_summary_instance = HistorySummary.from_json(json)
# print the JSON string representation of the object
print(HistorySummary.to_json())

# convert the object into a dict
history_summary_dict = history_summary_instance.to_dict()
# create an instance of HistorySummary from a dict
history_summary_from_dict = HistorySummary.from_dict(history_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


