var price_id = localStorage.getItem("price_id")
// console.log(price_id);
const notification_url = "http://127.0.0.1:5555/process-payment-success";

const notification = fetch(`${notification_url}/${price_id}`)
.then(response => response.json())
.then(data => {
    // console.log(data);
})

localStorage.clear()
const get_all_url = "http://127.0.0.1:5005/job";
const check_payment_url = "http://127.0.0.1:5006/check_payment"

const check_payment = fetch(check_payment_url)
.then(response => response.json())
.then(data => {
    // console.log(data);
})


const response = fetch(get_all_url).then(response => response.json())
.then(data => {
    var jobs = data["data"]
    // console.log(jobs);

    for (let index = 0; index < jobs.length; index++) {
        // console.log(jobs[index]);
        var curr_job = `job${index+1}`

        var job = jobs[index];
        var job_id = jobs[index]["_id"]["$oid"];
        // console.log(job_id);

        var job_title = job["Title"];
        var job_desc = job["Description"];
        var image = job["Image_Path"]
        var start_time = Number(job["Start_datetime"]);
        var end_time = Number(job["End_datetime"]);
        var status = job["Status"]
        var hourly_rate = job["Hourly_rate"]["$numberDecimal"]

        var start_format_date = new Date(start_time).toLocaleDateString("en-US");
        var start_format_time = new Date(start_time).toLocaleTimeString("en-SG");
        var end_format_date = new Date(end_time).toLocaleDateString("en-SG");
        var end_format_time = new Date(end_time).toLocaleTimeString("en-SG");

        // console.log(job_title, job_desc, image, start_format_date, start_format_time, end_format_date, end_format_time, status, hourly_rate);

        var temp_card_str = 
        `
        <div class="col-lg-4 col-md-6 my-2" id="${curr_job}">
            <div class="card h-100">
                <img src="${image}" class="card-img-top">
                <div class="card-body">
                <h5 class="card-title">${job_title}</h5>
                <p class="card-text">${job_desc}</p>
            </div>
            <div class="card-footer d-flex justify-content-between">
                <!-- View More Info Modal -->
                <button type="button" class="btn btn-info btn-sm" data-bs-toggle="modal" data-bs-target="#${curr_job}Modal" id="${curr_job}viewinfo">
                    View More Info
                </button>
                <!-- Modal -->
                <div class="modal fade" id="${curr_job}Modal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h1 class="modal-title fs-5" id="${curr_job}ModalLabel">${job_title}</h1>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body" id="${curr_job}_info">
                                <p>Job Description: ${job_desc}</p>
                                <p>Starting Date & Time: ${start_format_date} ${start_format_time}</p>
                                <p>Ending Date & Time: ${end_format_date} ${end_format_time}</p>
                                <p>Hourly Rate: $${hourly_rate}/hr</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>        
        `

        if (status == "Matched") {
            temp_card_str += 
            `
            <!-- Cancel Sitter -->
            <button class="btn btn-danger btn-sm" onclick="cancel_sitter('${job_id}')" id="${curr_job}cancel">Cancel Sitter</button>
            `
        }
        else{
            temp_card_str += 
            `            
            <!-- View Job Application Modals -->
            <button class="btn btn-primary btn-sm" id="${curr_job}all" onclick="fetch_applications('${job_id}')">View Applications</button>
            `
        }

        temp_card_str += 
        `
                </div>
            </div>
        </div>
        `

         document.getElementById("job_list").innerHTML += temp_card_str;
    }

    // fetch_applications(job_id);
    if (data.code === 404) {
        document.getElementById("job_list").innerHTML = "<h1 class='my-5 text-center'>You have no current job listings! Please create a job listing for your paw-some pets!</h1>"
    }
    else{
        // console.log(data);
    }
})
.catch(error => {
    console.log(error);
})


function fetch_applications(job_id) {

    // console.log(job_id);
    localStorage.setItem("job_id", job_id);
        // localStorage.setItem("applications", applications);
    window.location.href = "http://127.0.0.1:5500/view_applications.html"
}