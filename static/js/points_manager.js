document.addEventListener('DOMContentLoaded', () => {
    // Load points programs on page load
    loadPointsPrograms();

    // Handle program type selection
    const programTypeSelect = document.getElementById('programType');
    if (programTypeSelect) {
        programTypeSelect.addEventListener('change', function() {
            // Hide all program selects
            document.querySelectorAll('.program-select').forEach(select => {
                select.style.display = 'none';
            });
            
            // Show the selected program type's select
            const selectedType = this.value;
            if (selectedType) {
                const targetSelect = document.getElementById(`${selectedType}Select`);
                if (targetSelect) {
                    targetSelect.style.display = 'block';
                }
            }
        });
    }

    // Handle add points form submission
    const addProgramBtn = document.getElementById('addProgram');
    if (addProgramBtn) {
        addProgramBtn.addEventListener('click', async () => {
            const programType = document.getElementById('programType').value;
            const pointsBalance = document.getElementById('pointsBalance').value;
            
            let selectedProgram;
            if (programType === 'airline') {
                selectedProgram = document.getElementById('airlineProgram').value;
            } else if (programType === 'hotel') {
                selectedProgram = document.getElementById('hotelProgram').value;
            } else if (programType === 'creditcard') {
                selectedProgram = document.getElementById('creditcardProgram').value;
            }
            
            if (!selectedProgram || !pointsBalance) {
                alert('Please select a program and enter points balance');
                return;
            }

            try {
                const response = await fetch('/points/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        program_name: selectedProgram,
                        points_balance: parseInt(pointsBalance)
                    })
                });

                if (response.ok) {
                    // Reload points programs to show the new one
                    loadPointsPrograms();
                    // Reset form
                    document.getElementById('programType').value = '';
                    document.getElementById('pointsBalance').value = '';
                    document.querySelectorAll('.program-select').forEach(select => {
                        select.style.display = 'none';
                    });
                    // Close accordion
                    const accordion = document.querySelector('#addProgramCollapse');
                    const bsCollapse = bootstrap.Collapse.getInstance(accordion);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    }
                } else {
                    alert('Failed to add points program');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error adding points program');
            }
        });
    }
});

function createPointsProgramCard(programName, balance, programId) {
    const card = document.createElement('div');
    card.className = 'points-card mb-3';
    card.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">${programName}</h5>
                <div class="d-flex align-items-center justify-content-between">
                    <p class="card-text mb-0"><span class="points-balance">${parseInt(balance).toLocaleString()}</span> points</p>
                    <div class="btn-group">
                        <button class="btn btn-primary update-points-btn" data-program-id="${programId}">Update</button>
                        <button class="btn btn-danger delete-program-btn" data-program-id="${programId}">Delete</button>
                    </div>
                </div>
                <div class="update-points-form d-none mt-3" id="update-form-${programId}">
                    <div class="input-group">
                        <input type="number" class="form-control" placeholder="New point balance" min="0">
                        <button class="btn btn-success confirm-update" type="button">Save</button>
                        <button class="btn btn-secondary cancel-update" type="button">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add event listeners for update and delete buttons
    const updateBtn = card.querySelector('.update-points-btn');
    const deleteBtn = card.querySelector('.delete-program-btn');
    const updateForm = card.querySelector('.update-points-form');
    const confirmBtn = card.querySelector('.confirm-update');
    const cancelBtn = card.querySelector('.cancel-update');
    const pointsInput = card.querySelector('input[type="number"]');

    updateBtn.addEventListener('click', () => {
        updateForm.classList.remove('d-none');
        pointsInput.value = balance;
    });

    cancelBtn.addEventListener('click', () => {
        updateForm.classList.add('d-none');
    });

    confirmBtn.addEventListener('click', async () => {
        const newBalance = parseInt(pointsInput.value);
        if (isNaN(newBalance) || newBalance < 0) {
            alert('Please enter a valid points balance');
            return;
        }

        try {
            const response = await fetch('/points/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: programId,
                    points_balance: newBalance
                })
            });

            if (response.ok) {
                card.querySelector('.points-balance').textContent = newBalance.toLocaleString();
                updateForm.classList.add('d-none');
            } else {
                alert('Failed to update points balance');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error updating points balance');
        }
    });

    deleteBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to delete this points program?')) {
            try {
                const response = await fetch('/points/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        id: programId
                    })
                });

                if (response.ok) {
                    card.remove();
                } else {
                    alert('Failed to delete points program');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error deleting points program');
            }
        }
    });

    return card;
}

async function loadPointsPrograms() {
    try {
        const response = await fetch('/points/list');
        const data = await response.json();
        
        const container = document.getElementById('active-programs');
        if (container) {
            container.innerHTML = '';
            
            if (data.programs.length === 0) {
                container.innerHTML = '<p>No points programs added yet.</p>';
                return;
            }
            
            data.programs.forEach(program => {
                const card = createPointsProgramCard(program.program_name, program.points_balance, program.id);
                container.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading points programs:', error);
    }
}
