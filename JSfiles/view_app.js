const accept_application_route = "http://localhost:5100/accept_app";
const application_get_url = "http://localhost:5008/application/job";
const sitter_info_url = "http://localhost:5001/sitter"
const reject_sitter = "http://localhost:5008/application/reject_one"
// window.sessionStorage
var job_id = localStorage.getItem("job_id")

let sitters;

const app_response = fetch(`${application_get_url}/${job_id}`)
.then(response => response.json())
.then(data => {
    var temp_sitters = [];
    console.log(data);
    // return data
    applications = data.data;
    // window.sessionStorage
    // console.log(applications);
    var job_count = 0;
    for (let index = 0; index < applications.length; index++) {
        
        var curr_app = applications[index];
        var sitter_id = curr_app["SitterID"]
        var application_id = curr_app["_id"]["$oid"];
        // console.log(application_id);
        var app_status = curr_app["Status"]
        
        if (app_status === "Pending") {
            job_count += 1;
            var app_num = `app${job_count}`
            temp_sitters.push(sitter_id);

            temp_str = 
            `
            <div class="col-6 my-3">
                <div class="card" id='${application_id}'>
                    <img src="..." class="class-img-top" id="${app_num}image">
                    <div class="card-body">
                        <h5 class="card-title" id='${app_num}name'>Application ${job_count}</h5>
                        <h6 class="card-subtitle mb-2 text-body-secondary" id='${app_num}subtitle'>Card subtitle</h6>
                        <p class="card-text" id='${app_num}info'></p>
                        <button class="btn btn-success" id="${app_num}accept" onclick="accept_application('${application_id}')">Accept</button>
                        <button class="btn btn-danger" id="${app_num}reject" onclick="reject_application('${application_id}')">Reject</button>
                    </div>
                </div>
            </div>
            `

            document.getElementById("application_list").innerHTML += temp_str
            console.log(temp_sitters);
        }
        
    }

    if (job_count == 0) {
        document.getElementById("application_list").innerHTML = "<h1 class='my-5 text-center'>There are no applications for this job!</h1>"
    }

    populate_sitters(temp_sitters);

    populate_data(sitters)
    
})

function populate_sitters(temp_sitters){
    sitters = temp_sitters;
}




function populate_data(sitters_arr) {
    for (let index = 0; index < sitters_arr.length; index++) {
        curr_sitter = sitters_arr[index]["$oid"]
        // console.log(curr_sitter);

        const get_sitters = fetch(`${sitter_info_url}/${curr_sitter}`)
        .then(response => response.json())
        .then(data => {
            var sitter_data = data.data[0];
            // console.log(sitter_data);
            // console.log(index);
            var sitter_name = sitter_data["Name"]
            var sitter_desc = sitter_data["Description"]
            var sitter_rate = sitter_data["Hourly_rate"]
            var sitter_ph = sitter_data["Phone"]
            var sitter_postal = sitter_data["Postal"]
            var sitter_reg_pref = sitter_data["Region_preference"]
            var sitter_spec_preg = sitter_data["Species_preference"]
            var sitter_user_score = sitter_data["User_score"]
            var sitter_image = sitter_data["Image_Path"];


            // console.log(document.getElementById(`app${index+1}name`));
            // console.log(document.getElementById(`app${index+1}subtitle`));

            // console.log(`app${index+1}name`,`app${index+1}subtitle`);
            document.getElementById(`app${index+1}name`).innerText = sitter_name;
            document.getElementById(`app${index+1}subtitle`).innerText = sitter_desc;
            document.getElementById(`app${index+1}image`).src = sitter_image;

            var temp_str = 
            `
            <p>Phone Number: ${sitter_ph}</p>
            <p>Postal Code: ${sitter_postal}</p>
            <p>User Score: ${sitter_user_score}</p>
            <p>Hourly Rate: ${sitter_rate}</p>
            <p>Species Preference: ${sitter_spec_preg}</p>
            <p>Region Preferenece: ${sitter_reg_pref}</p>
            `
            
            document.getElementById(`app${index+1}info`).innerHTML = temp_str

        })
        
    }

    
}

function accept_application(item) {
    var confirmation = confirm(`Confirm sitter's application? We will notify the sitter about your application and update the current job listing`)
    const accept_response = fetch(`${accept_application_route}/${item}`,
    {
        method:"PUT",
        headers: {
            "Content-type":"application/json"
        }
    })
    .then(response => response)
    .then(data => {
        console.log(data);
    })

    location.reload()
}

function reject_application(item) {
    // console.log(sitters);
    rejection = confirm("Reject sitter? We will notify the sitter about your rejection and the application will not be shown to you again.")
    if (rejection == true) {
        const reject_app = fetch(`${reject_sitter}/${item}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })

        alert('You have successfully rejected the sitter.')
        location.reload(true)
    }
}