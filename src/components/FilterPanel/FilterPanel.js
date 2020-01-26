import React from "react";
import SchoolDistrictFilter from "../Filters/SchoolDistrictFilter";
import PrimaryGraphsChoose from "../Filters/PrimaryGraphsChoose";
import YearFilter from "../Filters/YearFilter";

// defaultSchoolOptions =

function FilterPanel(props) {
    // console.log('panel recieved school data' + props.data);

    return (
        <div className="filter-container">
            <SchoolDistrictFilter
                data={props.data}
                onOptionsChange={(selectedOptions, actionMeta) =>
                    props.onSchoolFilterChange(
                        selectedOptions,
                        actionMeta
                    )
                }
            />
            <YearFilter
                selectedYears={props.selectedYears}
                onYearChange={newYearSelection =>
                    props.onYearSelectionChange(newYearSelection)
                }
            />
            <PrimaryGraphsChoose
                selectedFilters={props.selectedFilters}
                onSelectionChange={newSelection =>
                    props.onGraphSelectionChange(newSelection)
                }
            />
        </div>
    );
}

export default FilterPanel;
