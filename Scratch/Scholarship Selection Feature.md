Scholarship Selection Feature

- Before building this feature, we must re-factor scholarship table so that it is simpler.  
	- We need to remove the JSON sub-structures from some of the fields, and simplify the way that this data is stored
	- We need to remove some fields which are not being used
	- We need to update the Schoolahoop frontend, so that it works with these structural changes
- The scholarship selection interface opens in a modal, over the school editing interface, by clicking a button.  
- The interface takes its preset state value from the state that the school being edited resides in. If a valid address has not been specified for the school, such that the state can be determined, then the user receives an error when trying to open this interface.
- Once interface is opened, the frontend contacts the API, and retrieves all scholarships for the school's state
	- Each scholarship row includes the title, and is expandable to show all details
	- If a scholarship was previously connected to the school being edited, this will be visually indicated, as described below.
- Each row has a checkbox region.  Clicking in this region causes the row to be selected, which means that the scholarship is connected to the school.  This is represented stylistically, e.g. with a color change, a checked box, etc.  The checkbox region is toggleable.
- There is a save button at the bottom of the scholarship rows.  Clicking it saves the indicated scholarship connections to the school, as well as removing connections which are no longer indicated, and closes the interface.