{%load static%}

<script>
    function send_rfx_model_initial(){
        // if (true){
            if ($('#table_filter_tab').val() !== 'all'){
            try {
                $($('.steps').children().children().children()[0]).click()
            } catch (error) {
                console.log('not found')
            }
            
            Swal.fire({
                title: "You did a great job!",
                text: "System is fetching supplier details. It may take a minute ",
                icon: "{% static '/images/loader.gif' %}",
                buttons: false,
                allowOutsideClick: false,
                closeOnClickOutside: false
            });
            $.get("{%url 'send_rfx'%}",{'Team':"{{Team}}"},function(data){
                $("#count_of_rfx").html(data.count)
                $('#notification').prop('checked',true)
                $('#notification').attr('checked','checked');
                console.log('notification')
                $('#next_quarter').prop('checked',true)
                $('#notification').attr('checked','checked');
                
                $('#this_quarter').prop('checked',false)
                $('#notification').attr('checked','');

                var supplier = data.disabled_supplier
                var text=''
                supplier.forEach(function (item) {
                    text += `
                    <tr class="table">
                    <td >${item.Supplier_Name}</td>
                    <td class=''>${item.Email}</td>
                    </tr>
                    `;
                }
                );
                
                var disabled_html=''
                data.suppliers_non_exists.forEach(function (item) {
                    disabled_html += `
                    <tr class="table">
                    <td >${item}</td>
                    </tr>
                    `;
                }
                );
                $('#disabled_supplier').html(
                    `
                    <thead>
                    <tr>
                    <th class='bg-primary bg-lighten-4 text-center text-white'>Supplier Name</th>
                    <th class='bg-primary bg-lighten-4 text-center text-white'>Email</th>
                    </tr>
                    </thead>
                    <tbody >
                    ${text}
                    </tbody>
                    `
                    )
                    $('#suppliers_non_exists').html(
                        `
                        <thead>
                        <tr>
                        <th class='bg-primary bg-lighten-4 text-center text-white'>Supplier Name</th>
                        </tr>
                        </thead>
                        <tbody >
                        ${disabled_html}
                        </tbody>
                        `
                        )
                        console.log(text)
                        var table_settings={
                            language: {
                                "emptyTable": "No Suppliers Found",
                            },
                            dom: 'Brtip',
                            lengthMenu: [
                                [10, 25, 50, -1],
                                ['10 rows', '25 rows', '50 rows', 'Show all']
                            ],
                            buttons: [{
                                text:'<i class="fa fa-download"></i> Excel',
                                extend: 'excelHtml5',
                                className:'btn-sm btn-outline-green square',
                                exportOptions: {
                                    columns: ':visible'
                                }
                            },
                        ],
                        orderCellsTop: true,
                    }
                    $("#disabled_supplier").DataTable(table_settings);
                    $("#suppliers_non_exists").DataTable(table_settings);
                    Swal.close()
                    $("#send_rfx_modal").modal('show')
                    if (data.count==0){
                        $("#send_rfq_button").attr('disabled',true)
                        $("#send_rfq_message").html('<span class=" danger float-right m-1 font-medium-2">RFQ has been already raised as Global/Regional,<br>Please match the Quote Type</span>')
                    }
                    else{
                        $("#send_rfq_button").attr('disabled',false)
                        $("#send_rfq_message").html('')
                    }
                    
                    
                
                document.getElementById("due_date").min = new Date().toISOString().slice(0,10);

            });
            distributor_selection()
        }
        
    }
    function distributor_selection(){
            $('#distributor_selection_container').html("<span class='font-medium-3'> System is loading distributor list. It may take a minute maximum <i class='ft-loader icon-spin text-left'></i></span>")
            $.get('{% url "distributor_selection"%}',{'Team':'{{Team}}'}, function(data) {
                $('#distributor_selection_container').html(data)
            });
        }
    $("#send_rfx_form").submit(function(e) {
            e.preventDefault(); 
            swal.fire({
                title: "Are you sure?",
                text: "For raising RFQ ",
                icon: "warning",
                buttons: true,
                dangerMode: true,
            })
            .then((input_user) => {
            if (input_user) {
                var form = $(this);
                var url = form.attr('action');
                var formData = new FormData(this);
                console.log(formData)
            $.ajax({
                type: "POST",
                url: url,
                data: formData, // serializes the form's elements.
                success: function(data) {
                    $("#send_rfx_modal").modal('hide');
                    swal.fire(data.message, {
                        icon: 'success',
                    })
                    
                    $('#Portfolio_table').DataTable().draw()
                },
                error: function(exception) {
                    swal.fire('Error session Time Out refresh the page', {
                        icon: 'error',
                        button: true,
                    })
                },
                cache: false,
                contentType: false,
                processData: false
            });

                } else {
                    swal.fire("Cancelled", {
                        timer: 1000
                    });
                }
            });
            
            //after inserting

        });
</script>