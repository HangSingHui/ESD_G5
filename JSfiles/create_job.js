// Dynamic Vue for Specs
const app = Vue.createApp({
    data() {
        return {
            spec_text: ''
        }
    },
    methods:{
        enterSpec(){
            document.getElementById("spec_placeholder").innerText = ""
            var spec_list = document.getElementById("spec_list")
            var curr_spec = document.getElementById("specification").value
            spec_list.setAttribute("class", "list-group")
            spec_list.innerHTML += 
            `<li class="list-group-item d-flex justify-content-between align-items-center" id="${curr_spec}">
                ${curr_spec}
            <button class="btn btn-danger" onclick="removeSpec('${curr_spec}')">X</button>
            </li>`
            document.getElementById("specification").value = ""

            this.spec_text = ""
        }
    }
})

const vm = app.mount('#app')
function updateTime() {
    const date = new Date()
    var year = date.getFullYear()
    var month = date.getMonth() + 1
    var day = date.getDate()
    var hours = date.getHours();
    var min = date.getMinutes();

    if (month < 10) {
        month = "0" + month
    }

    if (day < 10) {
        day = "0" + day
    }

    if (hours < 10) {
        hours = "0" + hours
    }

    if (min < 10) {
        min = "0" + min
    }

    document.getElementById("start-time").value = `${year}-${month}-${day}T${hours}:${min}`

    document.getElementById("start-time").min = `${year}-${month}-${day}T${hours}:${min}`

    document.getElementById("end-time").value = `${year}-${month}-${day}T${hours}:${min}`

    document.getElementById("end-time").min = `${year}-${month}-${day}T${hours}:${min}`
}

function removeSpec(spec) {
    document.getElementById(spec).remove()
    ifEmpty();
}

function ifEmpty() {
    var spec_list = document.getElementById("spec_list")
    if (spec_list.getElementsByTagName("li").length == 0) {
        document.getElementById("spec_placeholder").innerText = "No Specifications Entered"
        // console.log(document.getElementById("spec_placeholder"));
        spec_list.setAttribute("class", "list-group d-none")
    }
}

// Simulate that an owner has logged in 
var ownerID = '64291e7a06864f6b8cac1f28'

const create_route = "http://127.0.0.1:5400/createjob"

const fetch_pets_route = "http://127.0.0.1:5007/pets"

const pet_response = fetch(`${fetch_pets_route}/${ownerID}`)
.then(response => response.json())
.then(data => {

    if (data.code == 200) {
        pets = data.data;
        console.log(pets);

        li_string = "";

        for (let index = 0; index < pets.length; index++) {
            pet = pets[index];
            pet_id = pet["_id"]["$oid"]
            pet_name = pet["Name"]
            pet_breed = pet["Breed"]

            
            temp_li_string = `
            
            <li class="list-group-item">
                <input class="form-check-input me-1" type="checkbox" value="${pet_id}" id="${pet_id}">
                <label class="form-check-label">${pet_name} the ${pet_breed}</label>
            </li>
            `

            li_string += temp_li_string

            document.getElementById("pets").innerHTML = li_string;
        
        }
    }

    else if(data.code == 404){
        alert("You have no pets! Please register your pets before creating a job")
        document.getElementById("submit_button").setAttribute("class", "btn btn-primary disabled")
        document.getElementById("view_jobs").setAttribute("class", "btn btn-secondary disabled")
    }

    
})


function string_out(date_str) {
    return_arr = [];
    year = date_str.substring(0,4);
    month = date_str.substring(5,7);
    day = date_str.substring(8,10);
    hour = date_str.substring(11,13);
    minute = date_str.substring(15,17)

    return_arr.push(year)
    return_arr.push(month)
    return_arr.push(day)
    return_arr.push(hour)
    return_arr.push(minute)
    return_arr.push(0)

    // console.log(return_arr);

    return return_arr
}

function toTimestamp(year,month,day,hour,minute,second){
    var datum = new Date(Date.UTC(year,month-1,day,hour,minute,second));
    // console.log(datum);
    return datum.getTime()/1000;
}

function submit_job() {

    var job_title = document.getElementById("job_title").value;
    var job_desc = document.getElementById("job_desc").value;

    var payrate  = document.getElementById("payrate").value;
    
    var start_time_raw = document.getElementById("start-time").value;
    var end_time_raw = document.getElementById("end-time").value;

    var start_time_arr = string_out(start_time_raw);
    var start_time_unix = toTimestamp(start_time_arr[0],start_time_arr[1],start_time_arr[2],start_time_arr[3],start_time_arr[4],start_time_arr[5]);

    var end_time_arr = string_out(end_time_raw);
    var end_time_unix = toTimestamp(end_time_arr[0],end_time_arr[1],end_time_arr[2],end_time_arr[3],end_time_arr[4],end_time_arr[5]);

    var job_duration = end_time_unix - start_time_unix;
    var payout = job_duration * payrate;
    
    var pets = document.getElementById("pets");
    var pets_arr = [];
    
    var spec_arr = [];
    var spec_list = document.getElementById("spec_list");
    var files = document.getElementById("formFileMultiple").value;


    var checkboxes = pets.getElementsByTagName("input");
    for(pet of checkboxes){
        if (pet.checked == true) {
            pets_arr.push(pet.id);
        }
    }
    
    var specs = spec_list.getElementsByTagName("li");
    for(spec of specs){
        spec_arr.push(spec.id)
    }

    // Simulate the user sending in an image of the puppy 
    var image = "https://i.ibb.co/92ZMC6b/puppy.jpg"

    let jsonData = JSON.stringify({
        "OwnerID" : ownerID,
        "Created": "",
        "PetID" : pets_arr,
        "SitterID": "",
        "Title" : job_title,
        "Description" : job_desc,
        "Status" : "Open",
        "Start_datetime" : start_time_unix,
        "End_datetime" : end_time_unix,
        "Hourly_rate" : payrate,
        "Payout": payout,
        "Waitlist": "",
        "spec_list" : spec_arr,
        "Image_Path" : image,
    })

    const create_job = fetch(create_route,  {
        method : "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: jsonData
    })
    .then(response => response.json())
    .then(data => {
        // console.log(data);
        // result = data.data;
        // console.log(result);
        if (data.code === 201) {
            alert("Job has been successfully created!")
            window.location.reload()
        }
        else if (data.code === 500){
            alert("Job creation failed, please check that your fields are properly filled up and try again!")
        }

    })
}

function go_to_jobs() {
    window.location.href = "owner"
}